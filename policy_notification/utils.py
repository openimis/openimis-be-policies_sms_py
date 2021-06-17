from core.models import Language
from core.utils import get_first_or_default_language
from django.core.exceptions import ValidationError, PermissionDenied


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
