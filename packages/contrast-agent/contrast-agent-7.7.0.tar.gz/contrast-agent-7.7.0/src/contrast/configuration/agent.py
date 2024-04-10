# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from .config_builder import ConfigBuilder
from .config_option import ConfigOption
from contrast.utils.configuration_utils import str_to_bool
from contrast.utils.loggers import (
    DEFAULT_PROGNAME,
    DEFAULT_SECURITY_LOG_PATH,
    DEFAULT_SECURITY_LOG_LEVEL,
    DEFAULT_LOG_PATH,
    DEFAULT_LOG_LEVEL,
)


class Agent(ConfigBuilder):
    def __init__(self):
        super().__init__()

        self.default_options = [
            # Some logger default values are handled by the logger
            ConfigOption(
                canonical_name="agent.logger.level",
                default_value=DEFAULT_LOG_LEVEL,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="agent.logger.path",
                default_value=DEFAULT_LOG_PATH,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="agent.logger.stdout",
                default_value=False,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.logger.stderr",
                default_value=False,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.logger.progname",
                default_value=DEFAULT_PROGNAME,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="agent.security_logger.path",
                default_value=DEFAULT_SECURITY_LOG_PATH,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="agent.security_logger.level",
                default_value=DEFAULT_SECURITY_LOG_LEVEL,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="agent.python.enable_sys_monitoring",
                default_value=True,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.rewrite",
                default_value=True,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.policy_rewrite",
                default_value=True,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.pytest_rewrite",
                default_value=False,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.enable_automatic_middleware",
                default_value=True,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.enable_drf_response_analysis",
                default_value=True,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.enable_profiler",
                default_value=False,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.python.assess.use_pure_python_hooks",
                default_value=False,
                type_cast=str_to_bool,
            ),
            ConfigOption(
                canonical_name="agent.polling.app_activity_ms",
                default_value=30000,
                type_cast=int,
            ),
            ConfigOption(
                canonical_name="agent.polling.server_settings_ms",
                default_value=30_000,
                type_cast=int,
            ),
            ConfigOption(
                canonical_name="agent.polling.heartbeat_ms",
                default_value=30_000,
                type_cast=int,
            ),
        ]
