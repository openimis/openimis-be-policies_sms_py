from abc import ABC

from requests import PreparedRequest

from policies_sms.SMSGateway.RequestBuilders import BaseSMSBuilder
from policies_sms.SMSGateway.exceptions import GatewayConfigurationException
from policies_sms.apps import PoliciesSmsConfig


class SMSGatewayAbs(ABC):

    @property
    def provider_configuration_key(self):
        """
        :return: str
            Configuration key present in module_configuration.providers
        """
        raise NotImplementedError("provider_configuration_key not implemented")

    def get_provider_config_param(self, param):
        try:
            return self._gateway_provider_configuration[param]
        except KeyError as e:
            raise GatewayConfigurationException(type(self), param, self.provider_configuration_key) from e

    def send_sms(self, sms_message):
        raise NotImplementedError("send_sms not implemented")

    def build_request(self, builder: BaseSMSBuilder) -> PreparedRequest:
        builder.reset()
        builder.set_request_authorization(self.get_auth())
        builder.set_request_headers(self.get_headers())
        builder.set_request_method(self.get_method())
        builder.set_request_content(self.get_request_content())
        builder.set_request_url(self.get_request_url())
        return builder.get_request()

    def get_auth(self):
        raise NotImplementedError('get_auth not implemented')

    def get_headers(self):
        raise NotImplementedError('get_headers not implemented')

    def get_method(self):
        raise NotImplementedError('get_method not implemented')

    def get_request_content(self):
        raise NotImplementedError('get_request_content not implemented')

    def get_request_url(self):
        raise NotImplementedError('get_request_url not implemented')

    @property
    def _gateway_provider_configuration(self):
        return PoliciesSmsConfig.providers[self.provider_configuration_key]
