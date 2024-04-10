# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Using logger.info/debug/someOtherLevel() is not supported in this module. In order to get the correct
frame info, we must skip over functions called in this module and in vendored structlog. If logging is attempted,
incorrect frame info will be displayed on the log message if used in this file.

Use print(...) instead
"""
import asyncio

from contrast.agent import request_state
from contrast_vendor import structlog
from contrast.utils.configuration_utils import get_hostname

LOGGING_TO_BUNYAN_LOG_LEVEL_CONVERSION = {
    "critical": 60,
    "error": 50,
    "warning": 40,
    "info": 30,
    "debug": 20,
}


# TODO: PYT-3186 there should be no references to structlog.stdlib after this ticket is
# completed


def add_hostname_for_bunyan(logger, method_name, event_dict):
    event_dict["hostname"] = get_hostname()
    return event_dict


def add_request_id(logger, method_name, event_dict):
    event_dict["request_id"] = request_state.get_request_id()
    return event_dict


def rename_key_for_bunyan(old_name, new_name):
    def key_renamer(logger, method_name, event_dict):
        value = event_dict.get(old_name)
        if value and not event_dict.get(new_name):
            event_dict[new_name] = value
            del event_dict[old_name]

        return event_dict

    return key_renamer


def add_log_level_for_bunyan(logger, log_level, event_dict):
    """
    NOTE: Bunyan uses different log level integers than logging/structlog.
    """
    if log_level == "warn":
        # The stdlib has an alias
        log_level = "warning"

    new_value = LOGGING_TO_BUNYAN_LOG_LEVEL_CONVERSION.get(log_level, None)

    if new_value:
        event_dict["level"] = new_value

    return event_dict


def add_v_for_bunyan(logger, method_name, event_dict):
    event_dict["v"] = 0
    return event_dict


def add_progname_for_bunyan(logger, method_name, event_dict):
    """
    progname is the name of the process the agents uses in logs.
    The default value is Contrast Agent. progname will be used
    as the name of the logger as seen in the logs.
    """
    field = "name"
    current_handler = logger.handlers[0]

    if hasattr(current_handler.filters[0], field):
        progname = current_handler.filters[0].progname

        if progname:
            event_dict[field] = progname

    return event_dict


def add_asyncio_info(logger, method_name, event_dict):
    try:
        current_task = asyncio.current_task()

        # If no name has been explicitly assigned to the Task, the default asyncio Task implementation
        # generates a default name during instantiation.
        event_dict["asyncio_task_name"] = current_task.get_name()

        current_coro = current_task.get_coro()
        if hasattr(current_coro, "__name__"):
            event_dict["asyncio_coro_name"] = current_coro.__name__

        event_dict["asyncio_task_id"] = id(current_task)
    except Exception:
        # This can happen when there is no running event loop
        pass

    return event_dict


def init_structlog():
    """
    Initial configuration for structlog. This can still be modified by subsequent calls
    to structlog.configure.
    """
    structlog.configure(
        processors=[
            # TODO: PYT-3186 stop filtering here once we're using a filtering bound logger
            structlog.stdlib.filter_by_level,
            # exact key "time" required for bunyan parsing
            structlog.processors.TimeStamper(fmt="iso", key="time"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            add_log_level_for_bunyan,
            rename_key_for_bunyan("event", "msg"),
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.THREAD,
                ],
                additional_ignores=[
                    "contrast_vendor.structlog",
                    "contrast.utils.decorators",
                ],
            ),
            rename_key_for_bunyan("process", "pid"),
            add_request_id,
            add_asyncio_info,
            add_hostname_for_bunyan,
            add_progname_for_bunyan,
            add_v_for_bunyan,
            structlog.processors.format_exc_info,
            structlog.processors.StackInfoRenderer(
                additional_ignores=[
                    "contrast_vendor.structlog",
                    "contrast.utils.decorators",
                ]
            ),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        # TODO: PYT-3186 this will need to be something like PrintLoggerFactory()
        # or WriteLoggerFactory(). It also may need to change later.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # TODO: PYT-3186 use this wrapper class instead of one from structlib.stdlib
        # wrapper_class=structlog.make_filtering_bound_logger(log_level),
        wrapper_class=structlog.stdlib.BoundLogger,
        # TODO: PYT-3168 it's possible that using this option will prevent us from
        # being able to modify the logger on subsequent calls to structlog.configure.
        # If that happens, we need to make sure that not every logging call recreates
        # and configures a new logger instance.
        cache_logger_on_first_use=True,
    )
