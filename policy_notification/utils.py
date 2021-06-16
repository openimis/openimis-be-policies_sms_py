from core.models import Language
from core.utils import get_first_or_default_language
from django.core.exceptions import ValidationError, PermissionDenied


def get_default_sms_data():
    return {
        'approvalOfSMS': False,
        'languageOfSMS': get_first_or_default_language().code
    }


def validate_family_sms_data(data):
    sms_approval = data.get('approvalOfSMS', None)
    language_of_sms = data.get('languageOfSMS', None)

    if not isinstance(sms_approval, bool):
        raise ValidationError(F"approvalOfSMS has to be boolean, not {type(sms_approval)}")

    if not Language.objects.filter(code=language_of_sms).exists():
        raise ValidationError(F"Language code {language_of_sms} not listed in available language codes")

    data['approvalOfSMS'] = sms_approval
    data['languageOfSMS'] = language_of_sms
    return data
