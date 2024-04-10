# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from .config_builder import ConfigBuilder
from .config_option import ConfigOption
from contrast import AGENT_CURR_WORKING_DIR


class Api(ConfigBuilder):
    def __init__(self):
        super().__init__()

        self.default_options = [
            ConfigOption(canonical_name="api.url", default_value="", type_cast=str),
            ConfigOption(
                canonical_name="api.service_key",
                default_value="",
                type_cast=str,
                redacted=True,
            ),
            ConfigOption(
                canonical_name="api.api_key",
                default_value="",
                type_cast=str,
                redacted=True,
            ),
            ConfigOption(
                canonical_name="api.user_name",
                default_value="",
                type_cast=str,
                redacted=True,
            ),
            ConfigOption(
                canonical_name="api.request_audit.enable",
                default_value=False,
                type_cast=bool,
            ),
            ConfigOption(
                canonical_name="api.request_audit.path",
                default_value=AGENT_CURR_WORKING_DIR,
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="api.request_audit.requests",
                default_value=False,
                type_cast=bool,
            ),
            ConfigOption(
                canonical_name="api.request_audit.responses",
                default_value=False,
                type_cast=bool,
            ),
            ConfigOption(
                canonical_name="api.certificate.enable",
                default_value=False,
                type_cast=bool,
            ),
            ConfigOption(
                canonical_name="api.certificate.ignore_cert_errors",
                default_value=False,
                type_cast=bool,
            ),
            ConfigOption(
                canonical_name="api.certificate.ca_file",
                default_value="",
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="api.certificate.cert_file",
                default_value="",
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="api.certificate.key_file",
                default_value="",
                type_cast=str,
            ),
            ConfigOption(
                canonical_name="api.proxy.enable", default_value=False, type_cast=bool
            ),
            ConfigOption(
                canonical_name="api.proxy.url",
                default_value="",
                type_cast=str,
                redacted=True,
            ),
        ]
