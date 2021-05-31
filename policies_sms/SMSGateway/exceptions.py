
class GatewayConfigurationException(Exception):

    def __init__(self, gateway, parameter, provider_config):
        self.gateway = gateway
        self.message = F"{self.gateway}: " \
                       F"Parameter '{parameter}' not included in provider configuration {provider_config}."
        super().__init__(self.message)
