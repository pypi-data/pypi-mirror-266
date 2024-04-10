# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import base64
from http.cookiejar import DefaultCookiePolicy
import queue
import threading

from requests import Session
import contrast

from contrast.agent import scope
from contrast.agent.disable_reaction import DisableReaction
from contrast.agent.settings import Settings
from contrast.reporting import RequestAudit
from contrast.reporting.teamserver_messages.base_ts_message import (
    PYTHON,
    _b64url_stripped,
)
from contrast_vendor import structlog as logging

from .teamserver_messages import BaseTsMessage

logger = logging.getLogger("contrast")

REPORTING_CLIENT_THREAD_NAME = "ContrastReportingClient"

MAX_ATTEMPTS = 2
ERROR_STATUS_CODE = -1


# TODO: PYT-2865 RepartingClient is still essentially a singleton, but it's implemented
# using a function instead of a class. This still needs to be reworked.
class _ReportingClient(threading.Thread):
    # This must not be instantiated directly. Use get_reporting_client().
    def __init__(self):
        super().__init__(name=REPORTING_CLIENT_THREAD_NAME, daemon=True)

        self._stopper = object()  # sentinel sent over message_q to stop the thread
        self.message_q = queue.Queue(maxsize=128)
        self.settings = Settings()
        self.session = Session()
        # disable persisting cookies, per Architecture team recommendation.
        self.session.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))
        self.session.verify, self.session.cert = self.init_certs(self.settings)
        self.session.proxies = (
            self.settings.build_proxy_url() if self.settings.is_proxy_enabled else {}
        )
        server_name_b64 = _b64url_stripped(self.settings.get_server_name())
        server_path_b64 = _b64url_stripped(self.settings.get_server_path())
        server_type_b64 = _b64url_stripped(self.settings.get_server_type())
        auth_header = f"{self.settings.api_user_name}:{self.settings.api_service_key}"
        self.session.headers.update(
            {
                # the Authorization header must not have its padding stripped
                "Authorization": base64.urlsafe_b64encode(
                    auth_header.encode()
                ).decode(),
                "API-Key": self.settings.api_key,
                "Server-Name": server_name_b64,
                "Server-Path": server_path_b64,
                "Server-Type": server_type_b64,
                "X-Contrast-Agent": f"{PYTHON} {contrast.__version__}",
                "X-Contrast-Header-Encoding": "base64",
                "Application-Language": PYTHON,
                "Application-Name": _b64url_stripped(self.settings.app_name),
                "Application-Path": _b64url_stripped(self.settings.app_path),
            }
        )

        self.request_audit = (
            RequestAudit(self.settings.config)
            if self.settings.config.is_request_audit_enabled
            else None
        )
        if self.request_audit:
            self.request_audit.prepare_dirs()

    def init_certs(self, settings):
        verify = True
        cert = None
        if not settings.is_custom_cert_enabled:
            return verify, cert

        # custom certificate settings
        if settings.ca_file:
            verify = settings.ca_file
        if settings.client_cert_file and settings.client_private_key:
            cert = (
                settings.client_cert_file,
                settings.client_private_key,
            )
        if settings.ignore_cert_errors:
            verify = False
            logger.warning("Certificate verification is disabled.")

        # misconfig checks
        if (settings.client_cert_file and not settings.client_private_key) or (
            not settings.client_cert_file and settings.client_private_key
        ):
            logger.error(
                "Unable to communicate with Contrast. "
                "Certificate configuration is not set properly. "
                "Certificate PEM file or private key PEM file is missing.",
                cert_file=settings.client_cert_file,
                key_file=settings.client_private_key,
            )
            DisableReaction.run(settings)
            return verify, cert

        if not any(
            (settings.ca_file, settings.client_cert_file, settings.client_private_key)
        ):
            logger.warning(
                "Certificate configuration is enabled, but no certificate files are set."
            )

        return verify, cert

    def stop(self):
        self.message_q.put(self._stopper)
        self.join()

    def run(self):
        with scope.contrast_scope():
            logger.debug("Starting reporting thread")

            while self.settings.is_agent_config_enabled():
                try:
                    msg = self.message_q.get(block=True, timeout=5)
                    if msg is self._stopper:
                        break
                    response = self.send_message(msg)
                    msg.process_response(response, self)
                except queue.Empty:
                    pass
                except Exception as e:
                    logger.debug(
                        "WARNING: reporting client failed to send message", exc_info=e
                    )

    def send_message(self, msg):
        try:
            return self._send_message(msg)
        except Exception as e:
            logger.exception(
                "Failed to send %s message to Contrast: %s", msg.class_name, e
            )

        return None

    def _send_message(self, msg):
        """
        _send_message sends msg to Teamserver and returns the response.

        It is the caller's responsibility to handle any network exceptions.

        See send_message for the public interface, which handles exceptions.
        """
        status_code = ERROR_STATUS_CODE
        msg_name = msg.class_name
        logger.debug("Sending %s message to Teamserver", msg_name)

        url = msg.base_url + msg.path
        response = msg.request_method(
            self.session,
            url,
            json=msg.body,
            headers=msg.headers,
            allow_redirects=False,
            # environment variables can interfere with session fields, so
            # we set them explicitly as arguments:
            # https://github.com/psf/requests/issues/3829
            proxies=self.session.proxies,
            verify=self.session.verify,
            cert=self.session.cert,
        )

        try:
            status_code = response.status_code
            msg_success_status = response.json().get("success")
            messages = response.json().get("messages")
            if not msg_success_status:
                logger.error(
                    "Failure on Contrast UI processing request reason - (%s): %s",
                    messages,
                    status_code,
                )
        except Exception as e:
            if status_code == ERROR_STATUS_CODE:
                logger.debug(
                    "Failed to receive response from Contrast UI: %s ",
                    e,
                )

        logger.debug("Contrast UI response (%s): %s", msg_name, status_code)

        if self.request_audit:
            self.request_audit.audit(msg, response)

        msg.sent()
        return response

    def add_message(self, msg):
        if msg is None or not isinstance(msg, BaseTsMessage):
            return

        logger.debug("Adding msg to reporting queue: %s", msg.class_name)

        self.message_q.put(msg)

    def retry_message(self, msg):
        # Never send a message more than twice (original time plus one retry)
        # To prevent queue from filling up or causing memory issues.
        if msg.sent_count < MAX_ATTEMPTS:
            logger.debug("Re-enqueuing %s message", msg.class_name)
            self.add_message(msg)


_REPORTING_CLIENT = None


def get_reporting_client() -> _ReportingClient:
    """
    Gets the single instance of the reporting client. If the reporting client is not yet
    initialized, this function will initialize it too.
    """
    global _REPORTING_CLIENT
    if _REPORTING_CLIENT is None:
        _REPORTING_CLIENT = _ReportingClient()
    return _REPORTING_CLIENT


def clear_reporting_client() -> None:
    global _REPORTING_CLIENT
    _REPORTING_CLIENT = None
