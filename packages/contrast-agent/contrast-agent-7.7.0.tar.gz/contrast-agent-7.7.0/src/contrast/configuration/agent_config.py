# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.utils.configuration_utils import (
    DEFAULT_PATHS,
    load_yaml_config,
)
from contrast.utils.decorators import cached_property
from contrast_vendor import structlog as logging

from .agent import Agent
from .api import Api
from .application import Application
from .assess import Assess
from .inventory import Inventory
from .protect import Protect
from .root import Root
from .server import Server

logger = logging.getLogger("contrast")

DEFAULT_TEAMSERVER_TYPE = "EOP"
PUBLIC_SASS_TEAMSERVER_TYPES = {
    "app.contrastsecurity.com": "SAAS_DEFAULT",
    "app-agents.contrastsecurity.com": "SAAS_DEFAULT",
    "eval.contrastsecurity.com": "SAAS_POV",
    "eval-agents.contrastsecurity.com": "SAAS_POV",
    "ce.contrastsecurity.com": "SAAS_CE",
    "ce-agents.contrastsecurity.com": "SAAS_CE",
    "app.contrastsecurity.jp": "SAAS_TOKYO",
    "app-agents.contrastsecurity.jp": "SAAS_TOKYO",
    "cs": "SAAS_",
}

PRIVATE_SASS_TEAMSERVER_TYPE = "SAAS_CUSTOM"
PRIVATE_SASS_DOMAIN = ["contrastsecurity.com", "contrastsecurity.jp"]

TESTING_TEAMSERVER_TYPE = "TESTING"
TESTING_TEAMSERVER_NAMES = [
    "teamserver-darpa",
    "teamserver-darpa-agents",
    "alpha.contrastsecurity.com",
    "alpha-agents.contrastsecurity.com",
    "apptwo.contrastsecurity.com",
    "apptwo-agents.contrastsecurity.com",
    "teamserver-staging.contsec.jp",  # agents host name not defined yet.
    "teamserver-staging.contsec.com",
    "teamserver-staging-agents.contsec.com",
    "security-research.contrastsecurity.com",
    "security-research-agents.contrastsecurity.com",
    "teamserver-ops.contsec.com",  # agents host name not defined yet.
]


class AgentConfig:
    def __init__(self):
        self.config_status = None
        self._config = {}
        self.build_configs()
        self.check_for_api_config()

    def get(self, key):
        return self._config.get(key, None)

    def get_value(self, key):
        option = self.get(key)
        return option.value() if option else None

    def get_loggable_value(self, key):
        option = self.get(key)
        return option.loggable_value() if option else None

    def keys(self):
        return self._config.keys()

    def get_loggable_config(self):
        """
        The purpose of this function is to return a copy of the effective config with their resolved values rather than
        the ConfigOption object.
        """

        loggable_config = {}
        for key in self._config:
            loggable_config[key] = self.get_loggable_value(key)

        return loggable_config

    def log_config(self):
        loggable_config = self.get_loggable_config()

        logger.info("Current Configuration", **loggable_config)

    def build_configs(self):
        """
        For each class representing different parts of the config (Agent, etc),
        take the current config and apply any overriding logic such as overriding with
        environment keys/values.

        At this time the order of precedence is:
            os.env > Config yaml

        Meaning that a config value defined in os.environ must be used instead of
        the same config defined in contrast_security.yaml

        Note that CLI args (sys.argv) are not supported. This may change if the
        agent becomes a runner.
        """
        yaml_config = load_yaml_config(DEFAULT_PATHS)
        if not yaml_config:
            logger.info("No YAML config found; using default settings")

        builders = [Api, Agent, Application, Assess, Inventory, Protect, Root, Server]
        for builder in builders:
            status = builder().build(self._config, yaml_config)
            if status:
                # An error here indicates a failure with the type cast of the value
                self.config_status = status

    def check_for_api_config(self):
        """
        Validate api configurations were set.

        If any api configs are missing, log at ERROR and disable the agent.

        Returns the missing values or an empty list if none were missing.
        """

        api_keys = [
            "api.url",
            "api.service_key",
            "api.api_key",
            "api.user_name",
        ]

        missing_values = []
        for key in api_keys:
            option = self.get(key)
            if not option or option.value() in (None, ""):
                missing_values.append(key)

        if missing_values:
            msg = (
                f"Missing a required connection value for: {', '.join(missing_values)}"
            )
            logger.error(msg)
            self.config_status = "Unable to connect to Contrast, insufficient connection properties provided."
            enable_option = self.get("enable")
            enable_option.override_value = False

        return missing_values

    @property
    def session_id(self):
        return self.get_value("application.session_id")

    @session_id.setter
    def session_id(self, session_id):
        session_id_option = self.get("application.session_id")
        session_id_option.ui_value = session_id

        logger.debug(
            "Set session_id to %s", session_id_option.value(), direct_to_teamserver=1
        )

    def get_session_metadata(self):
        return self.get_value("application.session_metadata")

    @property
    def app_code(self):
        return self.get_value("application.code")

    @property
    def app_metadata(self):
        return self.get_value("application.metadata")

    @property
    def app_group(self):
        return self.get_value("application.group")

    @property
    def app_tags(self):
        return self.get_value("application.tags")

    @property
    def assess_tags(self):
        return self.get_value("assess.tags")

    @cached_property
    def is_request_audit_enabled(self):
        return self.get_value("api.request_audit.enable")

    @cached_property
    def assess_enabled(self):
        return self.get_value("assess.enable")

    @cached_property
    def should_pytest_rewrite(self):
        return self.assess_enabled and self.get_value("agent.python.pytest_rewrite")

    @cached_property
    def should_rewrite(self):
        return self.assess_enabled and self.get_value("agent.python.rewrite")

    @cached_property
    def should_apply_policy_rewrites(self):
        return self.should_rewrite and self.get_value("agent.python.policy_rewrite")

    @cached_property
    def should_enable_sys_monitoring(self):
        return self.get_value("agent.python.enable_sys_monitoring")

    @cached_property
    def enable_automatic_middleware(self) -> bool:
        return self.get_value("agent.python.enable_automatic_middleware")

    @cached_property
    def application_activity_polling_interval(self):
        return self.get_value("agent.polling.app_activity_ms")

    @cached_property
    def server_settings_poll_interval(self):
        return self.get_value("agent.polling.server_settings_ms")

    @cached_property
    def heartbeat_poll_interval(self):
        return self.get_value("agent.polling.heartbeat_ms")

    @cached_property
    def teamserver_type(self):
        url = self.get_value("api.url")

        if not url:
            return ""

        for name, ts_type in PUBLIC_SASS_TEAMSERVER_TYPES.items():
            if name in url:
                # This regex matches https://cs001.contrastsecurity.com
                r_url = re.match(r".*(cs\d{3})\..*", url)
                if r_url:
                    # and gets the second group which is the matched in brackets cs001
                    # adds it to the SAAS_ type and becomes SAAS_CS001
                    numbers = r_url.group(1).upper()

                    return ts_type + numbers

                return ts_type

        for name in TESTING_TEAMSERVER_NAMES:
            if name in url:
                return TESTING_TEAMSERVER_TYPE

        for name in PRIVATE_SASS_DOMAIN:
            if name in url:
                return PRIVATE_SASS_TEAMSERVER_TYPE

        return DEFAULT_TEAMSERVER_TYPE
