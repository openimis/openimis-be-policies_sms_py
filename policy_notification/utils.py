from core.models import Language
from core.utils import get_first_or_default_language
from django.core.exceptions import ValidationError, PermissionDenied

from policy_notification.notification_gateways.abstract_sms_gateway import NotificationGatewayAbs
from policy_notification.apps import PolicyNotificationConfig


def get_default_sms_data():
    return {
        'approvalOfNotification': False,
        'languageOfNotification': get_first_or_default_language().code
    }


def validate_family_sms_data(data):
    sms_approval = data.get('approvalOfNotification', None)
    language_of_notification = data.get('languageOfNotification', None)

    if not isinstance(sms_approval, bool):
        raise ValidationError(F"approvalOfNotification has to be boolean, not {type(sms_approval)}")

    if not Language.objects.filter(code=language_of_notification).exists():
        raise ValidationError(F"Language code {language_of_notification} not listed in available language codes")

    data['approvalOfNotification'] = sms_approval
    data['languageOfNotification'] = language_of_notification
    return data


def get_sms_providers():
    """
    In order for an notification provider to be used for sending notifications, it must meet two conditions:
    - it must be included in the configuration in the providers field,
    - secondly from the notification_gateways submodule there must be imported a class with the same name as the provider
    (the class name is case insensitive) that inherits from NotificationGatewayAbs, and implements the
    send_notification(notification_content, family_number) method.

    :return: list of notification providers eligible for sending notifications
    """
    notification_module = __import__("policy_notification.notification_gateways", fromlist=['*'])
    available_providers = dict(
        [(name, cls) for name, cls in notification_module.__dict__.items() if isinstance(cls, type)]
    )
    config_sms_providers = [v.lower() for v in PolicyNotificationConfig.providers.keys()]

    return [cls for name, cls in available_providers.items() if name.lower() in config_sms_providers]
