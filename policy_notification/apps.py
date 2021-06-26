from django.apps import AppConfig


MODULE_NAME = "policy_notification"

DEFAULT_CONFIG = {
    "providers": {
        "TextSMSProvider": {
            "DestinationFolder": "sent_sms"
        },
        "eGASMSGateway": {
            "GateUrl": "http://127.0.0.1:8000",
            "SmsResource": "/api/policy_notification/test_sms/",
            "PrivateKey": "",
            "UserId": "",
            "SenderId": "",
            "ServiceId": "",
            "RequestType": "",
            "HeaderKeys": "X-Auth-Request-Hash,X-Auth-Request-Id,X-Auth-Request-Type",
            "HeaderValues": "PrivateKey,UserId,RequestType"
        }
    }
}


class PolicyNotificationConfig(AppConfig):
    name = MODULE_NAME

    providers = {}

    def _configure_perms(self, cfg):
        PolicyNotificationConfig.providers = cfg["providers"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)
