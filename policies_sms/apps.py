from django.apps import AppConfig


MODULE_NAME = "policies_sms"

DEFAULT_CONFIG = {
    "providers": {
        "TextSMSProvider": {
            "DestinationFolder": "sent_sms"
        }
    }
}


class PoliciesSmsConfig(AppConfig):
    name = MODULE_NAME

    providers = []

    def _configure_perms(self, cfg):
        PoliciesSmsConfig.providers = cfg["providers"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)
