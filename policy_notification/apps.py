from django.apps import AppConfig

MODULE_NAME = "policy_notification"

DEFAULT_CONFIG = {
    "providers": {
        "TextNotificationProvider": {
            "DestinationFolder": "sent_notification"
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
    },
    "eligibleNotificationTypes": {
        "activation_of_policy": False,
        "starting_of_policy": False,
        "need_for_renewal": False,
        "expiration_of_policy": False,
        "reminder_after_expiration": False,
        "renewal_of_policy": False
    }
}


class PolicyNotificationConfig(AppConfig):
    name = MODULE_NAME

    providers = {}
    eligible_notification_types = {}

    def _configure_perms(self, cfg):
        PolicyNotificationConfig.providers = cfg["providers"]
        PolicyNotificationConfig.eligible_notification_types = cfg["eligibleNotificationTypes"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)
