# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
# pylint: disable=too-many-lines
from collections import defaultdict
import os
import pathlib
from datetime import datetime, timezone
import json
from urllib.parse import urlparse

from contrast import AGENT_CURR_WORKING_DIR

from contrast.utils.decorators import fail_quietly
from contrast.agent.exclusions import Exclusions, TsExclusion, ExclusionType
from contrast.agent.framework import Framework, Server
from contrast.agent.reaction_processor import ReactionProcessor
from contrast.agent.protect.rule import ProtectionRule
from contrast.configuration.config_option import (
    CONTRAST_UI_SRC,
    USER_CONFIGURATION_FILE_SRC,
    DEFAULT_VALUE_SRC,
)
from contrast.configuration.agent_config import AgentConfig
from contrast.utils.decorators import cached_property
from contrast.utils.loggers.logger import reset_agent_logger, STDOUT, STDERR
from contrast.utils.singleton import Singleton
from contrast.utils.string_utils import truncate
from contrast.utils.timer import now_ms
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")

ASSESS_STACKTRACES = "assess.stacktraces"
ASSESS_DISABLED_RULE_CONFIG_KEY = "assess.rules.disabled_rules"
EXPORTED_CONFIG_FILE_NAME = "contrast_connection.json"


class ServerFeatures:
    def __init__(self, features):
        self.features = features or {}

    @cached_property
    def log_file(self):
        return self.features.get("features", {}).get("logFile", "")

    @cached_property
    def log_level(self):
        return self.features.get("features", {}).get("logLevel", "")

    @cached_property
    def assess_enabled(self):
        return (
            self.features.get("features", {})
            .get("assessment", {})
            .get("enabled", False)
        )

    @cached_property
    def protect_enabled(self):
        return self.features.get("features", {}).get("defend", {}).get("enabled", False)


class ApplicationSettings:
    def __init__(self, settings_json=None):
        self._raw_settings = settings_json or {}

    @cached_property
    def disabled_assess_rules(self):
        return (
            self._raw_settings.get("settings", {})
            .get("assessment", {})
            .get("disabledRules", [])
        )

    @cached_property
    def protection_rules(self):
        return [
            ProtectRule(r)
            for r in self._raw_settings.get("settings", {})
            .get("defend", {})
            .get("protectionRules", [])
        ]

    @cached_property
    def session_id(self):
        return (
            self._raw_settings.get("settings", {})
            .get("assessment", {})
            .get("session_id", None)
        )

    @cached_property
    def sensitive_data_masking_policy(self):
        return self._raw_settings.get("settings", {}).get(
            "sensitive_data_masking_policy"
        )

    @cached_property
    def exclusions(self):
        """
        Build and return a plain list of TsExclusions based on raw application settings.
        TsExclusions represent the exclusions more or less exactly as they were given to
        us by teamserver.

        The list returned by this property will be converted into our own Exclusions
        class later, which is more useful when processing exclusion rules.
        """
        ts_exclusions = self._raw_settings.get("settings", {}).get("exceptions")
        if ts_exclusions is None:
            return None

        exclusions = []

        for exclusion in ts_exclusions.get("urlExceptions", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.URL_EXCLUSION_TYPE,
                    exclusion.get("name", ""),
                    exclusion.get("modes", []),
                    exclusion.get("matchStrategy", ""),
                    exclusion.get("protectionRules", []),
                    exclusion.get("assessmentRules", []),
                    exclusion.get("urls", []),
                )
            )

        for exclusion in ts_exclusions.get("inputExceptions", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.INPUT_EXCLUSION_TYPE,
                    exclusion.get("name", ""),
                    exclusion.get("modes", []),
                    exclusion.get("matchStrategy", ""),
                    exclusion.get("protectionRules", []),
                    exclusion.get("assessmentRules", []),
                    exclusion.get("urls", []),
                    exclusion.get("inputType", ""),
                    exclusion.get("inputName", ""),
                )
            )

        return exclusions

    # note: there are more fields on ApplicationSettings that we currently don't use


class ProtectRule:
    def __init__(self, protect_rule_json):
        self._raw_rule = protect_rule_json or {}

    @cached_property
    def id(self):
        return self._raw_rule.get("id", "")

    @cached_property
    def mode(self):
        raw_mode = self._raw_rule.get("mode", "OFF")
        raw_block_at_entry = self._raw_rule.get("blockAtEntry", False)

        # Common configuration uses lower case infinitives whereas TeamServer UI uses
        # capital present participles. This mapping has to handle both.
        return {
            "MONITOR": ProtectionRule.MONITOR,
            "MONITORING": ProtectionRule.MONITOR,
            "BLOCK": ProtectionRule.BLOCK,
            "BLOCKING": (
                ProtectionRule.BLOCK_AT_PERIMETER
                if raw_block_at_entry
                else ProtectionRule.BLOCK
            ),
            "BLOCK_AT_PERIMETER": ProtectionRule.BLOCK_AT_PERIMETER,
            "OFF": ProtectionRule.OFF,
        }[raw_mode.upper()]


class Settings(Singleton):
    def init(self, app_name=None, framework_name=None):
        """
        Agent settings for the entire lifetime of the agent.

        Singletons should override init, not __init__.
        """
        self.config = None
        self.config_features = {}
        self.exclusions = None
        self.last_server_update_time_ms = 0
        self.last_app_update_time_ms = 0
        self.heartbeat = None
        self.server_settings_poll = None
        self.framework = Framework(framework_name)
        self.server = Server()
        self.sys_module_count = 0

        # Server
        self.server_name = None
        self.server_path = None
        self.server_type = None

        self.exclusion_matchers = []

        # Rules
        self.protect_rules = dict()

        # circular import
        from contrast.agent.assess.rules.response.autocomplete_missing_rule import (
            AutocompleteMissingRule,
        )
        from contrast.agent.assess.rules.response.cache_controls_rule import (
            CacheControlsRule,
        )
        from contrast.agent.assess.rules.response.clickjacking_rule import (
            ClickjackingRule,
        )

        from contrast.agent.assess.rules.response.x_content_type_rule import (
            XContentTypeRule,
        )

        from contrast.agent.assess.rules.response.csp_header_missing_rule import (
            CspHeaderMissingRule,
        )

        from contrast.agent.assess.rules.response.x_xss_protection_disabled_rule import (
            XXssProtectionDisabledRule,
        )

        from contrast.agent.assess.rules.response.hsts_header_rule import HstsHeaderRule

        from contrast.agent.assess.rules.response.csp_header_insecure_rule import (
            CspHeaderInsecureRule,
        )

        from contrast.agent.assess.rules.response.parameter_pollution_rule import (
            ParameterPollutionRule,
        )

        self.assess_response_rules = [
            AutocompleteMissingRule(),
            CacheControlsRule(),
            ClickjackingRule(),
            XContentTypeRule(),
            CspHeaderMissingRule(),
            XXssProtectionDisabledRule(),
            HstsHeaderRule(),
            CspHeaderInsecureRule(),
            ParameterPollutionRule(),
        ]

        # Initialize config
        self.config = AgentConfig()
        self.sensitive_data_masking_policy = None

        # Initialize application metadata
        self.app_name = self.get_app_name(app_name)

        self.agent_runtime_window = now_ms()

        logger.info("Contrast Agent finished loading settings.")

    @cached_property
    def is_proxy_enabled(self):
        return self.config.get_value("api.proxy.enable")

    @cached_property
    def proxy_url(self):
        return self.config.get_value("api.proxy.url")

    @cached_property
    def api_url_scheme(self):
        scheme = urlparse(self.api_url).scheme
        return scheme

    @property
    def is_custom_cert_enabled(self):
        return self.config.get_value("api.certificate.enable")

    @property
    def ignore_cert_errors(self):
        return self.config.get_value("api.certificate.ignore_cert_errors")

    @property
    def ca_file(self):
        return self.config.get_value("api.certificate.ca_file")

    @property
    def client_cert_file(self):
        return self.config.get_value("api.certificate.cert_file")

    @property
    def client_private_key(self):
        return self.config.get_value("api.certificate.key_file")

    @cached_property
    def api_service_key(self):
        return self.config.get_value("api.service_key")

    @cached_property
    def api_url(self):
        """Normalizes the URL to remove any whitespace or trailing slash"""
        return self.config.get_value("api.url").strip().rstrip("/")

    @cached_property
    def api_key(self):
        return self.config.get_value("api.api_key")

    @cached_property
    def api_user_name(self):
        return self.config.get_value("api.user_name")

    def is_agent_config_enabled(self):
        if self.config is None:
            return True

        return self.config.get_value("enable")

    @cached_property
    def is_rewriter_enabled(self):
        return self.config.get_value("agent.python.rewrite")

    @cached_property
    def is_policy_rewriter_enabled(self):
        return self.config.should_apply_policy_rewrites

    @cached_property
    def is_profiler_enabled(self):
        return self.config.get_value("agent.python.enable_profiler")

    @cached_property
    def max_sources(self):
        return self.config.get_value("assess.max_context_source_events")

    @cached_property
    def max_propagation(self):
        return self.config.get_value("assess.max_propagation_events")

    @cached_property
    def max_vulnerability_count(self):
        """Max number of vulnerabilities per rule type to report for one
        agent run `time_limit_threshold` time period"""
        return self.config.get_value("assess.max_rule_reported")

    @cached_property
    def agent_runtime_threshold(self):
        return self.config.get_value("assess.time_limit_threshold")

    @cached_property
    def app_path(self):
        return self.config.get_value("application.path")

    @cached_property
    def app_version(self):
        return self.config.get_value("application.version")

    @cached_property
    def assess_event_detail(self) -> str:
        return self.config.get_value("assess.event_detail")

    @property
    def pid(self):
        """
        pid is used in our CMDi protect rule.

        pid must be unique for each worker process of an app.
        :return: int current process id
        """
        return os.getpid()

    def get_app_name(self, app_name):
        if self.config.get_value("application.name"):
            return self.config.get_value("application.name")

        return app_name if app_name else "root"

    def establish_heartbeat(self):
        """
        Initialize Heartbeat between Agent and TS if it has not been already initialized.
        """
        if self.heartbeat is None:
            # Circular import
            from contrast.agent.heartbeat_thread import HeartbeatThread

            self.heartbeat = HeartbeatThread()
            self.heartbeat.start()

    def establish_server_settings_poll(self):
        """
        Initialize Server Settings poll between Agent and TS if it has not been already initialized.
        """
        if self.server_settings_poll is None:
            # Circular import
            from contrast.agent.server_settings_poll import ServerSettingsPoll

            self.server_settings_poll = ServerSettingsPoll()
            self.server_settings_poll.start()

    def set_protect_assess_config_source(self, server_features):
        if self.config is None or server_features is None:
            return

        assess_option = self.config.get("assess.enable")
        if assess_option:
            assess_option.ui_value = server_features.assess_enabled

        protect_option = self.config.get("protect.enable")
        if protect_option:
            protect_option.ui_value = server_features.protect_enabled

    def apply_ts_feature_settings(self, response_body):
        server_features = ServerFeatures(response_body)
        self.log_server_features(server_features)
        self.update_sampling(server_features)
        self.update_logger_from_features(server_features)
        self.set_protect_assess_config_source(server_features)
        self.set_protect_rules()
        self.last_server_update_time_ms = now_ms()

    def process_ts_reactions(self, response_body):
        # App startup/activity wrap reactions in a settings dict whereas
        # Server startup/activity has it at the top level response dict
        reactions = response_body.get("settings", {}).get("reactions", None)

        if not reactions:
            reactions = response_body.get("reactions", None)

        if not reactions:
            return

        ReactionProcessor.process(reactions, self)

    def log_server_features(self, server_features):
        """
        Record server features received from teamserver
        """
        logger.debug(
            "Received updated server features logFile=%s logLevel=%s Protect=%s Assess=%s Sampling=%s",
            server_features.log_file,
            server_features.log_level,
            server_features.protect_enabled,
            server_features.assess_enabled,
            server_features.features.get("features", {})
            .get("assessment", {})
            .get("sampling", None),
        )

    @property
    def code_exclusion_matchers(self):
        return [x for x in self.exclusion_matchers if x.is_code]

    def load_exclusions_from_server(self, exclusions):
        if exclusions:
            self.exclusions = Exclusions(exclusions)

    def evaluate_exclusions(self, context, path):
        if self.exclusions:
            if self.exclusions.evaluate_url_exclusions(context, path):
                # Stop analyzing this endpoint since the URL exclusion applies
                return True

            if self.exclusions.input_exclusions:
                self.exclusions.set_input_exclusions_by_url(context, path)

        return False

    def apply_ts_app_settings(self, response_json):
        app_settings = ApplicationSettings(response_json)
        self.sensitive_data_masking_policy = app_settings.sensitive_data_masking_policy
        if app_settings.exclusions:
            self.load_exclusions_from_server(app_settings.exclusions)

        disabled_rule_option = self.config.get(ASSESS_DISABLED_RULE_CONFIG_KEY)
        disabled_rule_option.ui_value = app_settings.disabled_assess_rules

        # This is the only place session_id is set by TS.
        # If session id is set in the config, that value will be echoed back by TS
        if app_settings.session_id:
            id_option = self.config.get("application.session_id")
            id_option.ui_value = app_settings.session_id

        # In order to update all the rules based on latest TS settings, we need to make sure that any rule not
        # mentioned by TS, or more likely our tests, have their UI value reset.
        known_rules = []
        for rule in self.protect_rules:
            known_rules.append(rule)
        if app_settings.protection_rules:
            for definition in app_settings.protection_rules:
                rule_key = f"protect.rules.{definition.id}.mode"
                rule_option = self.config.get(rule_key)
                # Sometimes there are rules we don't know about that TeamServer sends us :(
                if rule_option:
                    rule_option.ui_value = definition.mode
                if definition.id in known_rules:
                    known_rules.remove(definition.id)
        for rule_name in known_rules:
            rule_key = f"protect.rules.{rule_name}.mode"
            rule_option = self.config.get(rule_key)
            if rule_option:
                rule_option.ui_value = None

    def update_logger_from_features(self, server_features):
        if server_features is None:
            return

        logger_reset = reset_agent_logger(
            server_features.log_file,
            server_features.log_level,
            self.config,
        )

        if logger_reset and self.config is not None:
            self.config.log_config()

    def is_inventory_enabled(self):
        """
        inventory.enable = false: Disables both route coverage and library analysis and reporting
        """
        return self.config.get_value("inventory.enable")

    def is_analyze_libs_enabled(self):
        """
        inventory.analyze_libraries = false: Disables only library analysis/reporting
        """
        return (
            self.config is not None
            and self.config.get_value("inventory.analyze_libraries")
            and self.is_inventory_enabled()
        )

    def is_assess_enabled(self):
        if self.config is None:
            return False

        return self.config.get_value("assess.enable")

    def is_protect_enabled(self):
        if self.config is None:
            return False
        return self.config.get_value("protect.enable")

    def set_protect_rules(self):
        if not self.is_protect_enabled():
            self.protect_rules = dict()
            return

        from contrast.agent.protect.rule.rules_builder import build_protect_rules

        self.protect_rules = build_protect_rules()

    def get_server_name(self):
        """
        Hostname of the server

        Default is socket.gethostname() or localhost
        """
        if self.server_name is None:
            self.server_name = self.config.get_value("server.name")

        return self.server_name

    def get_server_path(self):
        """
        Working Directory of the server

        Default is root
        """
        if self.server_path is None:
            self.server_path = self.config.get_value("server.path") or truncate(
                AGENT_CURR_WORKING_DIR
            )

        return self.server_path

    def get_server_type(self):
        """
        Web Framework of the Application either defined in common config or via discovery.
        """
        if self.server_type is None:
            self.server_type = (
                self.config.get_value("server.type") or self.framework.name_lower
            )

        return self.server_type

    @property
    def response_scanning_enabled(self):
        return self.is_assess_enabled() and self.config.get_value(
            "assess.enable_scan_response"
        )

    def is_assess_rule_disabled(self, rule_id):
        """
        Rules disabled in config override all disabled rules from TS per common config
        """
        disabled_rules = self.config.get_value(ASSESS_DISABLED_RULE_CONFIG_KEY)
        return disabled_rules is not None and rule_id in disabled_rules

    def enabled_response_rules(self):
        return (
            [
                rule
                for rule in self.assess_response_rules
                if not self.is_assess_rule_disabled(rule.name)
            ]
            if self.response_scanning_enabled
            else []
        )

    def is_collect_stacktraces_all(self):
        return (
            self.config is not None
            and self.config.get_value(ASSESS_STACKTRACES) == "ALL"
        )

    def is_collect_stacktraces_some(self):
        return (
            self.config is not None
            and self.config.get_value(ASSESS_STACKTRACES) == "SOME"
        )

    def is_collect_stacktraces_none(self):
        return (
            self.config is not None
            and self.config.get_value(ASSESS_STACKTRACES) == "NONE"
        )

    def build_proxy_url(self):
        if self.proxy_url:
            # self.api_url_scheme is the key of the scheme we are proxying
            # self.proxy_url is the actual proxy url and port
            # https://requests.readthedocs.io/en/latest/user/advanced/#proxies
            return {self.api_url_scheme: self.proxy_url}

        return {}

    def update_sampling(self, server_features=None):
        if server_features is None:
            return

        server_sampling = (
            server_features.features.get("features", {})
            .get("assessment", {})
            .get("sampling")
        )
        if server_sampling is None:
            return

        sampling_enable = self.config.get("assess.sampling.enable")
        if sampling_enable:
            sampling_enable.ui_value = server_sampling.get("enabled", None)
        sampling_baseline = self.config.get("assess.sampling.baseline")
        if sampling_baseline:
            sampling_baseline.ui_value = server_sampling.get("baseline", None)
        sampling_request_frequency = self.config.get(
            "assess.sampling.request_frequency"
        )
        if sampling_request_frequency:
            sampling_request_frequency.ui_value = server_sampling.get("frequency", None)
        sampling_window_ms = self.config.get("assess.sampling.window_ms")
        if sampling_window_ms:
            sampling_window_ms.ui_value = server_sampling.get("window", None)
        logger.debug(
            "Updated sampling setting with TeamServer sampling settings: %s",
            server_sampling,
        )

    @cached_property
    def contrast_ui_status(self):
        config_name = "enable"
        error_msg = "Unable to connect to Contrast; configuration details from the Contrast UI will not be included."

        enable_option = self.config.get(config_name)
        if enable_option is None or enable_option.ui_value is False:
            # This indicates we were told to shut down by Contrast UI
            return error_msg

        # TODO: PYT-2612 seems like _send_startup_msg_with_retries in agent_state always returns true
        return None

    def generate_effective_config(self):
        """
        The purpose of this function is to export as many of the configuration values found in AgentConfig
        to the effective_config list. This list will be logged to disk. Some values that where set using
        the Contrast UI where saved to AgentConfig in attempt to have a single place storing all settings.

        In some cases this wasn't immediately feasible due to when and how we reload those settings
        """
        status = self.contrast_ui_status or self.config.config_status or "Success"
        report_creation_time = datetime.now(timezone.utc).isoformat()
        config = {
            "report_create": report_creation_time,
            "config": {
                "status": status,
                "effective_config": [],
                "user_configuration_file": [],
                "environment_variable": [],
                "contrast_ui": [],
            },
        }

        effective_config = config["config"]["effective_config"]
        env_config = config["config"]["environment_variable"]
        ui_config = config["config"]["contrast_ui"]

        user_config = defaultdict(list)

        for key in self.config.keys():
            option = self.config.get(key)
            if option is None:
                continue

            # The spec states this value is not included if we can't communicate with Contrast UI
            if (
                option.source() == CONTRAST_UI_SRC
                and self.contrast_ui_status is not None
            ):
                continue

            value = option.loggable_value()

            # If the value is unset and has no default value, we should skip it.
            # For instance, if a proxy isn't set, there's no reason to report those configuration values.
            if option.source() == DEFAULT_VALUE_SRC and value in ("", "[]"):
                continue

            config_entry = {
                "canonical_name": option.canonical_name,
                "name": option.provided_name(),
                "source": option.source(),
                "value": value,
            }
            if option.source() == USER_CONFIGURATION_FILE_SRC:
                config_entry["filename"] = option.file_name()

            effective_config.append(config_entry)

            if option.env_value is not None:
                config_entry = {
                    "canonical_name": option.canonical_name,
                    "name": option.provided_name(),
                    "value": option.to_string(option.env_value),
                }
                env_config.append(config_entry)
            if option.ui_value is not None:
                config_entry = {
                    "canonical_name": option.canonical_name,
                    # provided name is only for env vars
                    "name": option.canonical_name,
                    "value": option.to_string(option.ui_value),
                }
                ui_config.append(config_entry)
            if option.file_values:
                for val, filename in zip(option.file_values, option.file_sources):
                    config_entry = {
                        "canonical_name": option.canonical_name,
                        # provided name is only for env vars
                        "name": option.canonical_name,
                        "value": option.to_string(val),
                    }
                    user_config[filename].append(config_entry)

        config["config"]["user_configuration_file"] = [
            {"path": filename, "values": values}
            for filename, values in user_config.items()
        ]

        return config

    @fail_quietly("Failed to export effective config")
    def log_effective_config(self):
        """
        If we have a directory to which to log safely, we are to add the effective configuration json file to that
        location. For other instances, such as STDOUT or un-writable directories, there is no need to write the file as
        the configuration is contained in our standard logs.
        """
        if (
            self.config.get_value("agent.logger.stdout")
            or self.config.get_value("agent.logger.stderr")
            or self.config.get_value("agent.logger.path") in (STDOUT, STDERR)
        ):
            return
        path = pathlib.Path(self.config.get_value("agent.logger.path")).parent.resolve()
        filename = f"{path}/{EXPORTED_CONFIG_FILE_NAME}"

        try:
            with open(filename, "w") as f:
                json.dump(self.generate_effective_config(), f, indent=4)
        except PermissionError as perm_error:
            logger.warning(
                "Failed to export effective config",
                filename=filename,
                error=str(perm_error),
            )
            return
