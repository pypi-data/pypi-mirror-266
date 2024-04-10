# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import copy
from dataclasses import dataclass
from itertools import chain
from pathlib import PurePath
import re
import reprlib
import threading
from typing import Any, Callable, Dict, List, Optional, Sequence, Type
from contrast.agent.assess.tag import Tag

from contrast.agent.policy.constants import (
    OBJECT,
    RETURN,
    TRIGGER_TYPE,
    CREATION_TYPE,
)

from contrast.agent.assess.truncate import truncate_tainted_string
from contrast.agent.assess.utils import get_properties

from contrast.agent.policy.policy_node import PolicyNode
from contrast.agent.settings import Settings
from contrast.api.trace_event import (
    TraceEvent,
    TraceEventObject,
    ParentObjectId,
    TraceEventSource,
)
from contrast.utils.assess.duck_utils import len_or_zero
from contrast.utils.base64_utils import B64_NONE_STRING, base64_encode
from contrast.utils.stack_trace_utils import (
    build_stack,
    clean_stack,
)
from contrast.utils.timer import now_ms
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")

INIT = "__init__"
INITIALIZERS = (INIT, "__new__")
NONE_STRING = str(None)


class Repr(reprlib.Repr):
    def repr_str(self, x, level):
        return x

    def repr_bytes(self, x, level):
        return x.decode(errors="replace")

    def repr_bytearray(self, x, level):
        return self.repr_bytes(x, level)

    def repr_instance(self, x, level):
        return f"{x.__class__.__module__}.{x.__class__.__qualname__}@{id(x):#x}"

    def repr_bool(self, x, level):
        return str(x)

    def repr_float(self, x, level):
        return str(x)

    def repr_NoneType(self, x, level):
        return "None"

    def repr_Pattern(self, x, level):
        return (
            self.repr1(x.pattern, level)
            if isinstance(x, re.Pattern)
            else self.repr_instance(x, level)
        )

    def repr_PurePath(self, x, level):
        return str(x) if isinstance(x, PurePath) else self.repr_instance(x, level)

    repr_PosixPath = repr_WindowsPath = repr_Path = repr_PurePosixPath = (
        repr_PureWindowsPath
    ) = repr_PurePath


class FullRepr(Repr):
    def repr_StringIO(self, x, level):
        return x.getvalue()

    def repr_BytesIO(self, x, level):
        return x.getvalue().decode(errors="replace")


class TruncatedRepr:
    def __init__(self, _repr: Repr):
        _repr = copy.copy(_repr)
        _repr.maxlevel = 3
        self._repr = _repr.repr

    def repr(self, obj: object):
        s = self._repr(obj)
        if len(s) > 103:
            s = s[:50] + "..." + s[-50:]
        return s


base_repr = Repr()
obj_repr = TruncatedRepr(base_repr)


def set_event_detail(detail: str):
    global obj_repr
    obj_repr = TruncatedRepr(base_repr if detail == "minimal" else FullRepr())


@dataclass
class Field:
    type: Type
    value: str

    def __init__(
        self, obj, typ=None, repr_func: Callable[[object], str] = obj_repr.repr
    ):
        self.type = typ or type(obj)
        self.value = repr_func(obj)


class ContrastEvent:
    """
    This class holds the data about an event in the application
    We'll use it to build an event that TeamServer can consume if
    the object to which this event belongs ends in a trigger.
    """

    ATOMIC_ID = 0

    def __init__(
        self,
        node: PolicyNode,
        tagged: Any,
        self_obj: Optional[Any],
        ret: Optional[Any],
        args: Sequence[Any],
        kwargs: Dict[str, Any],
        parent_ids: List[int],
        possible_key=None,
        source_type=None,
        source_name=None,
    ):
        self.node = node
        self._init_tagged(tagged, possible_key, args, kwargs)
        self.source_type = source_type
        self.source_name = source_name
        self.parent_ids = parent_ids
        ret = self._update_init_return(node, self_obj, ret)
        self.obj = Field(self_obj) if self_obj is not None else None
        self.ret = Field(ret) if ret is not None else None
        self.args = [Field(arg) for arg in args] if args is not None else None
        self.kwargs = (
            [Field(f"{k}={obj_repr.repr(v)}", typ=type(v)) for k, v in kwargs.items()]
            if kwargs is not None
            else None
        )

        # These are needed only at trigger-time but values must be set at init.
        self.time = now_ms()
        self.thread = threading.current_thread().ident
        self.event_id = ContrastEvent._atomic_id()

        self.event_action = self.node.build_action()

        self._raw_stack = build_stack() if self._should_get_stack else []

        # This must happen at init for stream events to work.
        self._update_method_information()

    def _init_tagged(self, tagged: Any, possible_key=None, args=None, kwargs=None):
        """
        Initialize properties related to tagging.
        - self.tagged
        - self.taint_location
        - self.span_override
        """
        self.taint_location = possible_key or self._find_taint_location(args, kwargs)
        if self.taint_location and isinstance(tagged, dict):
            tagged = tagged.get(self.taint_location, None)
        tags = None
        self.tagged_props = get_properties(tagged)
        if self.tagged_props and isinstance(tagged, str):
            self.tagged_props.cleanup_tags()
            tags = [tag for tag in chain.from_iterable(self.tagged_props.tags.values())]
            tagged_repr, truncate_tags = truncate_tainted_string(tagged, tags)
            self.tagged = Field(tagged_repr, repr_func=base_repr.repr)
            self.tags_override = truncate_tags
        else:
            self.tagged = Field(tagged, repr_func=base_repr.repr)
            self.tags_override = (
                None
                if len(self.tagged.value) == len_or_zero(tagged)
                else (Tag(len(self.tagged.value), 0),)
            )

    @property
    def _should_get_stack(self):
        """
        Determine if event.stack should be populated or not.

        Get stacktrace for the event EXCEPT if
          1. the node explicitly indicates not to collect a stacktrace, which is the
                case for WSGI environ sources
          2. assess.stacktraces is configured to NONE
          3. assess.stacktraces is configured to SOME and event action is not
                creation or trigger


        :return: bool if to get stacktrace
        """
        settings = Settings()

        reportable_actions = (
            TraceEvent.Action[CREATION_TYPE],
            TraceEvent.Action[TRIGGER_TYPE],
        )

        if (
            self.node.skip_stacktrace
            or settings.is_collect_stacktraces_none()
            or (
                settings.is_collect_stacktraces_some()
                and self.event_action not in reportable_actions
            )
        ):
            return False

        return True

    @classmethod
    def _atomic_id(cls):
        ret = cls.ATOMIC_ID
        cls.ATOMIC_ID += 1
        return ret

    def _find_taint_location(self, args=None, kwargs=None):
        """
        Find the location of the tagged value in the event. This is used to determine
        where the tagged value is in the event, so that we can mark it up in TeamServer.
        """
        if len(self.node.targets) == 1:
            return self.node.targets[0]
        for loc in chain(self.node.targets, self.node.sources):
            if loc in (OBJECT, RETURN):
                return loc
            if isinstance(loc, int) and args and loc < len(args):
                return loc
            if isinstance(loc, str) and kwargs and loc in kwargs:
                return loc

        return None

    def _update_method_information(self):
        """
        For nicer reporting, we lie about the tagged value. For example, a call to
        split() returns a list of strings: ["foo", "bar"]. In the properties for "foo",
        the split event shows a return value of only "foo" instead of the whole list.
        """
        if self.taint_location is None:
            # This would be for trigger nodes without source or target. Trigger rule was
            # violated simply by a method being called. We'll save all the information,
            # but nothing will be marked up, as nothing need be tracked.
            return

        if self.taint_location == OBJECT:
            self.obj = self.tagged
            return

        if self.taint_location == RETURN:
            self.ret = self.tagged

    def to_reportable_event(self):
        """
        Convert a ContrastEvent to a TraceEvent.
        """
        event = TraceEvent()

        event.type = self.node.node_type
        event.action = self.event_action
        event.timestamp_ms = self.time
        event.thread = str(self.thread)
        event.tags = self.node.tags

        self._build_all_event_objects(event)

        event.stack = clean_stack(self._raw_stack, depth=20)

        safe_source_name = self.source_name if self.source_name is not None else ""
        event.field_name = safe_source_name

        if self.source_type:
            event.event_sources.append(self.build_source_event(safe_source_name))

        event.object_id = int(self.event_id)

        if self.parent_ids:
            for parent_id in self.parent_ids:
                parent = ParentObjectId()
                parent.id = parent_id
                event.parent_object_ids.append(parent)

        self._build_complete_signature(event)
        self._validate_event(event)

        return event

    def _update_init_return(self, node, obj, ret):
        """
        For purposes of pretty reporting in Teamserver, we will say the
        `__init__` instance method return the `self` object (the object getting
        instantiated) instead of `None`, even though `None` is the return value of
        `__init__` methods.

        This will not apply if the node is not a class (it's possible someone
        creates a module level function called `__init__` or if the return
        value is already populated (for safety).
        """
        if node.method_name == INIT and node.class_name is not None:
            ret = ret or obj
        return ret

    def build_source_event(self, safe_source_name: str) -> TraceEventSource:
        """
        Create a new TraceEventSource
        """
        trace_event_source = TraceEventSource()

        trace_event_source.type = self.source_type
        trace_event_source.name = safe_source_name

        return trace_event_source

    def _set_event_source_and_target(self, event: TraceEvent):
        """
        We have to do a little work to figure out what our TS appropriate
        target is. To break this down, the logic is as follows:
        1) If my node has a target, work on targets. Else, work on sources.
           Per TS law, each node must have at least a source or a target.
           The only type of node w/o targets is a Trigger, but that may
           change.
        2) I'll set the event's source and target to TS values.
        """
        if self.node.targets:
            event.source = self.node.ts_valid_source
            event.target = self.node.ts_valid_target
        elif self.node.sources:
            event.source = self.node.ts_valid_target or self.node.ts_valid_source

    def _build_all_event_objects(self, event: TraceEvent):
        """
        First populate event.source and event.target
        Then populate fields of event.object, event.ret, and event.args (contains both
        args and kwargs for python) which are each `TraceEventObject`s
        """
        self._set_event_source_and_target(event)

        event.object.value = (
            base64_encode(self.obj.value) if self.obj else B64_NONE_STRING
        )
        event.ret.value = base64_encode(self.ret.value) if self.ret else B64_NONE_STRING
        if self.args:
            event.args = [
                TraceEventObject(arg.value if arg else B64_NONE_STRING)
                for arg in self.args
            ]
        if self.kwargs:
            event_kwargs = [
                TraceEventObject(kwarg.value if kwarg else B64_NONE_STRING)
                for kwarg in self.kwargs
            ]
            event.args.extend(event_kwargs)

        self._add_taint_ranges(event, self.taint_location)

    def _add_taint_ranges(self, event: TraceEvent, taint_location: str):
        """
        Populate event.taint_ranges
        """
        if taint_location is None or not self.tagged_props:
            return

        event.taint_ranges = self.tagged_props.tags_to_ts_obj(self.tags_override)

        # For now, only the taint_target needs to be officially marked as tracked.
        # This means that agent-tagged strings may not be marked as "tracked" for TS.
        # This may change in the future if we change the corresponding TS endpoint; in
        # that case, use recursive_is_tracked for each TraceEventObject.
        if taint_location == OBJECT:
            event_obj = event.object
        elif taint_location == RETURN:
            event_obj = event.ret
        elif isinstance(taint_location, int):
            event_obj = event.args[taint_location]
        elif isinstance(taint_location, str):
            event_obj = event.args[-1]

        event_obj.tracked = True

    def _build_complete_signature(self, event: TraceEvent):
        return_type = self.ret.type.__name__ if self.ret is not None else NONE_STRING

        event.signature.return_type = return_type
        # We don't want to report "BUILTIN" as a module name in Team Server
        event.signature.class_name = self.node.location.replace("BUILTIN.", "")
        event.signature.method_name = self.node.method_name

        if self.args:
            event.signature.arg_types.extend(
                [
                    arg.type.__name__ if arg is not None else NONE_STRING
                    for arg in self.args
                ]
            )

        if self.kwargs:
            event.signature.arg_types.extend(
                [
                    kwarg.type.__name__ if kwarg is not None else NONE_STRING
                    for kwarg in self.kwargs
                ]
            )

        event.signature.constructor = self.node.method_name in INITIALIZERS

        # python always returns None if not returned
        event.signature.void_method = False

        if not self.node.instance_method:
            event.signature.flags = 8

    def _validate_event(self, event: TraceEvent):
        """
        TS is not able to render a vulnerability correctly if the source string index 0
        of the trigger event, ie event.source, is not a known one.

        See TS repo DataFlowSnippetBuilderVersion1.java:buildMarkup

        :param event: TraceEvent
        :return: None
        """
        allowed_trigger_sources = ["O", "P", "R"]
        if (
            event.action == TraceEvent.Action[TRIGGER_TYPE]
            and event.source[0] not in allowed_trigger_sources
        ):
            # If this is logged, check the node in policy.json corresponding to
            # this event and how the agent has transformed the source string
            logger.debug("WARNING: trigger event TS-invalid source %s", event.source)
