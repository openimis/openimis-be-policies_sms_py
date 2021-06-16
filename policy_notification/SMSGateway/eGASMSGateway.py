import requests

from policy_notification.SMSGateway.RequestBuilders import BaseSMSBuilder
from policy_notification.SMSGateway.abstract_sms_gateway import SMSGatewayAbs


class EGASMSGateway(SMSGatewayAbs):

    def __init__(self, builder=BaseSMSBuilder()):
        self.builder = builder

        # Last sent message
        self.message_sent = None

    @property
    def provider_configuration_key(self):
        return "eGASMSGateway"

    def send_sms(self, sms_message, builder=None):
        self.message_sent = sms_message

        builder = builder or self.builder
        request = self.build_request(builder)
        s = requests.Session()
        response = s.send(request)
        return response

    def get_auth(self):
        # Gateway uses XAuthHeaders assigned in headers
        return None

    def get_headers(self):
        header_keys = self.get_provider_config_param('HeaderKeys')
        header_values = self.get_provider_config_param('HeaderValues')
        if header_values != '' and header_keys != '':
            header_dict = dict(zip(header_keys.split(','), header_values.split(',')))
            header_dict_with_actual_values = {k: self.get_provider_config_param(v) for k, v in header_dict.items()}
            return header_dict_with_actual_values
        else:
            return {}

    def get_method(self):
        return 'POST'

    def get_request_content(self):
        return self.message_sent

    def get_request_url(self):
        return self.get_provider_config_param('GateUrl') + self.get_provider_config_param('SmsResource')
