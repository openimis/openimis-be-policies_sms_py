import base64
import datetime
import json
import logging
import requests
import hmac
import hashlib

from policy_notification.notification_gateways.RequestBuilders import BaseSMSBuilder
from policy_notification.notification_gateways.abstract_sms_gateway import NotificationGatewayAbs, \
    NotificationSendingResult


logger = logging.getLogger(__name__)


class EGASMSGateway(NotificationGatewayAbs):
    # Use utc+3 timezone
    _GATEWAY_TIMEZONE_OFFSET = 3

    def __init__(self, builder=BaseSMSBuilder()):
        self.builder = builder

        # Last sent message
        self.message_sent = None
        self.family_number = None
        self.sending_time = None

    def header_values_evaluation(self):
        return {
            'UserId': self.get_provider_config_param('UserId'),
            'RequestType': self.get_provider_config_param('RequestType'),
            'HashMessage1': self.create_request_hash()
        }

    @property
    def provider_configuration_key(self):
        return "eGASMSGateway"

    def send_notification(self, notification_content, family_number=None, builder=None) -> NotificationSendingResult:
        self.message_sent = notification_content
        self.family_number = family_number
        self.sending_time = datetime.datetime.now(tz=datetime.timezone.utc)
        self.sending_time += datetime.timedelta(hours=self._GATEWAY_TIMEZONE_OFFSET)

        builder = builder or self.builder
        request = self.build_request(builder)
        s = requests.Session()
        response = s.send(request)
        success = (response and response.status_code == 200)
        if response and response.status_code != 200:
            logger.warning(f"Notification request sent, but resulted in "
                           f"status {response.status_code}, "
                           f"content of response: {response.content}")
        return NotificationSendingResult(response, success=success)

    def get_auth(self):
        # Gateway uses XAuthHeaders assigned in headers
        return None

    def get_headers(self):
        header_keys = self.get_provider_config_param('HeaderKeys')
        header_values = self.get_provider_config_param('HeaderValues')
        if header_values != '' and header_keys != '':
            header_dict = dict(zip(header_keys.split(','), header_values.split(',')))
            header_dict_with_actual_values = \
                {k: self.header_value(v) for k, v in header_dict.items()}
            return header_dict_with_actual_values
        else:
            return {}

    def get_method(self):
        return 'POST'

    def get_request_content(self):
        return json.dumps({
            'data': self._get_message_content(self.message_sent),
            'datetime': self.sending_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def get_request_url(self):
        return self.get_provider_config_param('GateUrl') + self.get_provider_config_param('SmsResource')

    def header_value(self, header_key):
        try:
            return self.header_values_evaluation().get(header_key)
        except KeyError as e:
            logger.error(f"Failed to get header value representation for header {header_key}. Request not sent")
            raise

    def create_request_hash(self):
        key = self.get_provider_config_param('PrivateKey')
        message = self._get_message_content(self.message_sent)

        signature = hmac.new(
            str.encode(key, encoding='ascii'),
            str.encode(message, encoding='ascii'),
            hashlib.sha256
        )
        header_hash = base64.b64encode(signature.digest()).decode()
        return header_hash

    def _get_message_content(self, message):
        return json.dumps({
            "message": message,
            "datetime": self.sending_time.strftime('%Y-%m-%d %H:%M:%S'),
            "sender_id": self.get_provider_config_param('SenderId'),
            "mobile_service_id": self.get_provider_config_param('ServiceId'),
            "recipients": self.family_number
        })

