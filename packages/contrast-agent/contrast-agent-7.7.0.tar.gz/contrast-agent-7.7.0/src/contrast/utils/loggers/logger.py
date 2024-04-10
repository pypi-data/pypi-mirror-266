# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import sys

import logging as stdlib_logging

import contrast
from contrast.assess_extensions import cs_str
from contrast.utils.loggers.structlog import init_structlog
from contrast.utils.configuration_utils import get_hostname
from contrast.utils.namespace import Namespace
from contrast.configuration.config_option import CONTRAST_UI_SRC, DEFAULT_VALUE_SRC

from contrast_vendor import structlog

from . import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_PROGNAME,
    LOGGER_NAME,
    SECURITY_LOGGER_NAME,
)

STDOUT = "STDOUT"
STDERR = "STDERR"


class module(Namespace):
    initialized: bool = False


def setup_basic_agent_logger(level=stdlib_logging.INFO):
    """
    Setup a logger without any user-supplied configuration, with defaults:
        1. log to stdout
        2. log in INFO level
        3. with default progname

    The logger created here is expected to be overridden with config values
    provided later on in the middleware creation cycle.
    """
    if not module.initialized:
        logger = stdlib_logging.getLogger(LOGGER_NAME)
        logger.addHandler(stdlib_logging.StreamHandler(sys.stdout))
        _set_handler(logger, "STDOUT", DEFAULT_PROGNAME)
        logger.setLevel(level)

        init_structlog()
        module.initialized = True

    return structlog.getLogger(LOGGER_NAME)


def setup_agent_logger(config):
    """
    Initialize the agent logger with configurations.
    :param config: instance of AgentConfig or dict
    :return: None
    """
    if config.get_value("agent.logger.stdout"):
        path = STDOUT
    elif config.get_value("agent.logger.stderr"):
        path = STDERR
    else:
        path = config.get_value("agent.logger.path")
    level = config.get_value("agent.logger.level").upper()

    logger = stdlib_logging.getLogger(LOGGER_NAME)

    _set_logger_info(logger, config, path, level)

    cs_str.initialize_logger(structlog.getLogger(LOGGER_NAME))


def setup_security_logger(cfg):
    config = cfg if cfg else {}

    if not config.get_value("protect.enable"):
        return

    path = config.get_value("agent.security_logger.path")
    level = config.get_value("agent.security_logger.level").upper()

    logger = stdlib_logging.getLogger(SECURITY_LOGGER_NAME)

    _set_level(logger, level)

    handler = _get_handler(path)
    logger.addHandler(handler)

    fmt = (
        f"%(asctime)s {get_hostname()} CEF:0|Contrast Security|Contrast Agent Python|{contrast.__version__}|"
        "SECURITY|%(message)s|%(level)s|'pri=%(rule_id)s' 'src=%(source_ip)s' 'spt=%(source_port)s' "
        "'request=%(request_url)s' 'requestMethod=%(request_method)s' 'app=%(application)s' "
        "'outcome=%(outcome)s'"
    )

    formatter = stdlib_logging.Formatter(fmt)
    handler.setFormatter(formatter)


def security_log_msg(msg, app_name, rule_name, outcome):
    context = contrast.CS__CONTEXT_TRACKER.current()
    ip = port = url = method_name = "-"

    logger = stdlib_logging.getLogger(SECURITY_LOGGER_NAME)

    if context is not None:
        ip = context.request.client_addr or "-"
        port = context.request.host_port
        method_name = context.request.method
        url = context.request.path

    log_context = dict(
        level=logger.level,
        rule_id=rule_name,
        source_ip=ip,
        source_port=port,
        request_url=url,
        request_method=method_name,
        application=app_name,
        outcome=outcome,
    )

    logger.warning(msg, extra=log_context)


def reset_agent_logger(log_path, log_level, config):
    """
    Reset agent logger path and/or level after the logger has already been created.

    Also note that progname is never reset so we use the one already set to the logger.

    :return: Bool if any logger value is reset
    """
    logger = stdlib_logging.getLogger(LOGGER_NAME)

    is_reset = False
    current_path_option = config.get("agent.logger.path") if config else None
    # A configuration path can be changed if the config is unset or we're not set directly to STDOUT or STDERR
    changeable_path = not config or not (
        config.get_value("agent.logger.stdout")
        or config.get_value("agent.logger.stderr")
    )
    if log_path:
        need_update = current_path_option is None or (
            log_path != current_path_option.value()
            and current_path_option.source() in (CONTRAST_UI_SRC, DEFAULT_VALUE_SRC)
            and changeable_path
        )
        if current_path_option:
            current_path_option.ui_value = log_path
        if need_update:
            current_handler = logger.handlers[0]
            progname = current_handler.filters[0].progname
            _set_handler(logger, log_path, progname)
            # print so it shows up in STDOUT
            print(f"Contrast Agent Logger updated path to {log_path}")
            is_reset = True

    current_level_option = config.get("agent.logger.level") if config else None
    if log_level:
        need_update = current_level_option is None or (
            log_level != current_level_option.value()
            and current_level_option.source() in (CONTRAST_UI_SRC, DEFAULT_VALUE_SRC)
        )
        if current_level_option:
            current_level_option.ui_value = log_level
        if need_update:
            _set_level(logger, log_level)

            # print so it shows up in STDOUT
            print(f"Contrast Agent Logger updated level to {log_level}")
            # Avoid circular import
            from contrast.agent.agent_lib import update_log_options

            if update_log_options(log_level):
                print(f"Contrast Agent Lib Logger updated level to {log_level}")
            is_reset = True
    return is_reset


def _set_logger_info(logger, config, path, level):
    progname = config.get_value("agent.logger.progname")

    _set_handler(logger, path, progname)
    _set_level(logger, level)


def _set_handler(logger, path, progname):
    """
    A logger's handler is what determines where the log records will be printed to
    and what format they will have.

    To reset a handler, we delete the existing handlers and create a new one.

    CONTRAST-39746 defined the datetime format as ISO_8601. The one here is
    without ms as the logger doesn't natively support both ms and time zone at this time.
    """
    handler = _get_handler(path)
    program_filter = AgentFilter(progname=progname)
    handler.addFilter(program_filter)

    # empty all handlers so there is only one stdlib_logging handler with this config
    logger.handlers = []
    logger.addHandler(handler)


def _get_handler(path):
    if path == STDOUT:
        handler = stdlib_logging.StreamHandler(sys.stdout)
    elif path == STDERR:
        handler = stdlib_logging.StreamHandler(sys.stderr)
    else:
        try:
            if dirname := os.path.dirname(path):
                os.makedirs(dirname, exist_ok=True)
            handler = stdlib_logging.FileHandler(path)
        except Exception as e:
            print(e, file=sys.stderr)
            # path could be '' or None
            handler = stdlib_logging.StreamHandler()

    return handler


def _set_level(logger, level: str) -> None:
    if level.upper() == "TRACE":
        level = "DEBUG"
        print("Contrast Python Agent: TRACE logging is equivalent to DEBUG")
    try:
        logger.setLevel(level)
    except ValueError:
        # this fails validation if the level is an invalid value
        logger.setLevel(DEFAULT_LOG_LEVEL)


class AgentFilter(stdlib_logging.Filter):
    def __init__(self, progname=None):
        self.progname = progname
        super().__init__()

    def filter(self, record):
        record.progname = self.progname
        return super().filter(record)
