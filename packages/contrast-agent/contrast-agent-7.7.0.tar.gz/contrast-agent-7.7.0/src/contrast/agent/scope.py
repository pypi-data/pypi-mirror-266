# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Controller for global scope state

Basically we use scoping to prevent us from assessing our own code. Scope
improves performance but it also prevents us from accidentally recursing
inside our analysis code. For example, we don't want to inadvertently cause
string propagation events while we're doing string building for reporting
purposes.
"""
from typing import Callable, Generator

import functools
import contextlib

from contrast.assess_extensions import cs_str


def enter_contrast_scope() -> None:
    """
    Enter contrast scope

    Contrast scope is global. It should prevent us from taking *any*
    further analysis action, whether it be propagation or evaluating
    triggers.
    """
    cs_str.enter_scope(cs_str.CONTRAST_SCOPE)


def enter_propagation_scope() -> None:
    """
    Enter propagation scope

    While in propagation scope, prevent any further propagation actions.
    Basically this means that no string propagation should occur while in
    propagation scope.
    """
    cs_str.enter_scope(cs_str.PROPAGATION_SCOPE)


def enter_trigger_scope() -> None:
    """
    Enter trigger scope

    While in trigger scope, prevent analysis inside of any other trigger
    methods that get called.
    """
    cs_str.enter_scope(cs_str.TRIGGER_SCOPE)


def exit_contrast_scope() -> None:
    cs_str.exit_scope(cs_str.CONTRAST_SCOPE)


def exit_propagation_scope() -> None:
    cs_str.exit_scope(cs_str.PROPAGATION_SCOPE)


def exit_trigger_scope() -> None:
    cs_str.exit_scope(cs_str.TRIGGER_SCOPE)


def in_contrast_scope() -> bool:
    return cs_str.in_scope(cs_str.CONTRAST_SCOPE)


def in_propagation_scope() -> bool:
    return cs_str.in_scope(cs_str.PROPAGATION_SCOPE)


def in_trigger_scope() -> bool:
    return cs_str.in_scope(cs_str.TRIGGER_SCOPE)


@contextlib.contextmanager
def contrast_scope() -> Generator[None, None, None]:
    cs_str.enter_scope(cs_str.CONTRAST_SCOPE)
    try:
        yield
    finally:
        cs_str.exit_scope(cs_str.CONTRAST_SCOPE)


@contextlib.contextmanager
def propagation_scope() -> Generator[None, None, None]:
    cs_str.enter_scope(cs_str.PROPAGATION_SCOPE)
    try:
        yield
    finally:
        cs_str.exit_scope(cs_str.PROPAGATION_SCOPE)


@contextlib.contextmanager
def trigger_scope() -> Generator[None, None, None]:
    cs_str.enter_scope(cs_str.TRIGGER_SCOPE)
    try:
        yield
    finally:
        cs_str.exit_scope(cs_str.TRIGGER_SCOPE)


def with_contrast_scope(orig_func: Callable) -> Callable:
    @functools.wraps(orig_func)
    def contrast_scope_wrapper(*args, **kwargs):
        cs_str.enter_scope(cs_str.CONTRAST_SCOPE)
        try:
            return orig_func(*args, **kwargs)
        finally:
            cs_str.exit_scope(cs_str.CONTRAST_SCOPE)

    return contrast_scope_wrapper


def with_propagation_scope(orig_func: Callable) -> Callable:
    @functools.wraps(orig_func)
    def propagation_scope_wrapper(*args, **kwargs):
        cs_str.enter_scope(cs_str.PROPAGATION_SCOPE)
        try:
            return orig_func(*args, **kwargs)
        finally:
            cs_str.exit_scope(cs_str.PROPAGATION_SCOPE)

    return propagation_scope_wrapper


def with_trigger_scope(orig_func: Callable) -> Callable:
    @functools.wraps(orig_func)
    def trigger_scope_wrapper(*args, **kwargs):
        cs_str.enter_scope(cs_str.TRIGGER_SCOPE)
        try:
            return orig_func(*args, **kwargs)
        finally:
            cs_str.exit_scope(cs_str.TRIGGER_SCOPE)

    return trigger_scope_wrapper


###################################################
# Convenience functions not needed for all scopes #
###################################################


def in_contrast_or_propagation_scope():
    """Indicates we are in either contrast scope or propagation scope"""
    return cs_str.in_contrast_or_propagation_scope()


@contextlib.contextmanager
def pop_contrast_scope():
    """
    Context manager that pops contrast scope level and restores it when it exits

    Scope is implemented as a stack. If the thread is in contrast scope at the time
    this is called, the scope level will be reduced by one for the lifetime of the
    context manager. If the prior scope level was 1, this has the effect of temporarily
    disabling contrast scope. The original scope level will be restored when the
    context manager exits. If the thread is **not** already in contrast scope when this
    is called, it has no effect.
    """
    was_in_scope = cs_str.in_scope(cs_str.CONTRAST_SCOPE)
    # This has no effect if we're not already in scope
    cs_str.exit_scope(cs_str.CONTRAST_SCOPE)
    try:
        yield
    finally:
        # For safety, only restore scope if we were in it to begin with
        if was_in_scope:
            cs_str.enter_scope(cs_str.CONTRAST_SCOPE)
