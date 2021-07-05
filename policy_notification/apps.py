from django.apps import AppConfig

MODULE_NAME = "policy_notification"

DEFAULT_CONFIG = {
    "providers": {
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
        },
        "TextNotificationProvider": {
            "DestinationFolder": "sent_notification"
        }
    },
    "eligibleNotificationTypes": {
        "activation_of_policy": False,
        "starting_of_policy": False,
        "need_for_renewal": False,
        "expiration_of_policy": False,
        "reminder_after_expiration": False,
        "renewal_of_policy": False
    },
    "family_policy_notification_report_perms": ["131224"],
    "trigger_time_interval_hours": 4,
    "trigger_first_call_hour": 8,
    "trigger_last_call_hour": 20,
    "reminder_before_expiry_days": 5,
    "reminder_after_expiry_days": 5
}


class PolicyNotificationConfig(AppConfig):
    name = MODULE_NAME

    providers = {}
    eligible_notification_types = {}
    family_policy_notification_report_perms = []
    trigger_time_interval_hours = 4
    trigger_first_call_hour = 8
    trigger_last_call_hour = 20
    reminder_before_expiry_days = 5
    reminder_after_expiry_days = 5

    def _configure_perms(self, cfg):
        PolicyNotificationConfig.providers = cfg["providers"]
        PolicyNotificationConfig.eligible_notification_types = cfg["eligibleNotificationTypes"]
        PolicyNotificationConfig.family_policy_notification_report_perms = \
            cfg["family_policy_notification_report_perms"]
        PolicyNotificationConfig.trigger_time_interval_hours = cfg['trigger_time_interval_hours']
        PolicyNotificationConfig.trigger_first_call_hour = cfg['trigger_first_call_hour']
        PolicyNotificationConfig.trigger_last_call_hour = cfg['trigger_last_call_hour']
        PolicyNotificationConfig.reminder_before_expiry_days = cfg['reminder_before_expiry_days']
        PolicyNotificationConfig.reminder_after_expiry_days = cfg['reminder_after_expiry_days']

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)
