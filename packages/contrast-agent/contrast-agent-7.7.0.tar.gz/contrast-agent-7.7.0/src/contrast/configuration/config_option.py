# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

ENVIRONMENT_VARIABLE_SRC = "ENVIRONMENT_VARIABLE"
USER_CONFIGURATION_FILE_SRC = "USER_CONFIGURATION_FILE"
DEFAULT_VALUE_SRC = "DEFAULT_VALUE"
CONTRAST_UI_SRC = "CONTRAST_UI"


class ConfigOption:
    def __init__(self, canonical_name, default_value, type_cast, redacted=False):
        self.canonical_name = canonical_name
        self.default_value = default_value
        self.type_cast = type_cast
        self.name = None
        self.override_value = None
        self.env_value = None
        self.file_values = None
        self.file_sources = None
        self.ui_value = None
        self.redacted = redacted

    def value(self):
        if self.override_value is not None:
            return self.override_value
        if self.env_value is not None:
            return self.env_value
        if self.file_values:
            return self.file_values[0]
        if self.ui_value is not None:
            return self.ui_value
        return self.default_value

    def source(self):
        if self.env_value is not None:
            return ENVIRONMENT_VARIABLE_SRC
        if self.file_values:
            return USER_CONFIGURATION_FILE_SRC
        if self.ui_value is not None:
            return CONTRAST_UI_SRC
        return DEFAULT_VALUE_SRC

    def file_name(self):
        return (
            self.file_sources[0]
            if self.file_sources and self.source() == USER_CONFIGURATION_FILE_SRC
            else None
        )

    def provided_name(self):
        if self.name is not None:
            return self.name
        return self.canonical_name

    def loggable_value(self):
        return self.to_string(self.value())

    def to_string(self, raw_value):
        # If the value is empty, just return empty String.
        if raw_value in (None, ""):
            return ""
        # If the option is sensitive, like an API credential, we do not log or report it.
        if self.redacted:
            return "**REDACTED**"
        str_value = str(raw_value)
        # If the option is an enum, we need to clean it up.
        if str_value and str_value.startswith("ProtectionRule."):
            return str_value.lstrip("ProtectionRule.").lower()
        return str_value

    def clear(self):
        """
        This is used as a convenience method during testing to ensure a clean slate.
        """
        self.override_value = None
        self.env_value = None
        self.file_values = None
        self.ui_value = None
        self.file_sources = None
