# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import requests

from .base_ts_message import BaseTsAppMessage
from .effective_config import EffectiveConfig
from contrast.utils.decorators import fail_loudly
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")


class ApplicationStartup(BaseTsAppMessage):
    def __init__(self):
        super().__init__()

        self.body = {
            "instrumentation": {
                "protect": {"enable": self.settings.is_protect_enabled()}
            }
        }

        if self.settings.config.get_session_metadata():
            self.body.update(
                {"session_metadata": self.settings.config.get_session_metadata()}
            )

        if self.settings.config.app_metadata:
            self.body.update({"metadata": self.settings.config.app_metadata})

        if self.settings.config.app_code:
            self.body.update({"code": self.settings.config.app_code})

        if self.settings.config.session_id:
            self.body.update({"session_id": self.settings.config.session_id})

        if self.settings.config.app_tags:
            self.body.update({"tags": self.settings.config.app_tags})

        if self.settings.config.app_group:
            self.body.update({"group": self.settings.config.app_group})

    @property
    def name(self):
        return "application-startup"

    @property
    def path(self):
        return "applications/create"

    @property
    def expected_response_codes(self):
        return [200]

    @property
    def disable_agent_on_401_and_408(self):
        return True

    @property
    def request_method(self):
        return requests.Session.put

    @fail_loudly("Failed to process ApplicationStartup response")
    def process_response(self, response, reporting_client):
        if not self.process_response_code(response, reporting_client):
            return

        body = response.json()

        self.settings.apply_ts_app_settings(body)
        self.settings.process_ts_reactions(body)
        self.settings.log_effective_config()
        if reporting_client is not None and self.settings.is_agent_config_enabled():
            reporting_client.add_message(EffectiveConfig())
