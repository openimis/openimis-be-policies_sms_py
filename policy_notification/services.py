import logging
from datetime import datetime

from core.schema import signal_mutation_module_after_mutating, signal_mutation_module_validate
from core.models import Language
from django.core.exceptions import ValidationError
from typing import List

from policy_notification.models import FamilySMS
from insuree.models import Family

from policy_notification.utils import validate_family_sms_data, get_default_sms_data
logger = logging.getLogger(__name__)


def create_family_sms_policy(family_uuid: str, family_sms_data=None) -> FamilySMS:
    """
    Create new familySMS for given family.
    :param family_uuid: UUID of family for which FamilySMS will be created
    :param family_sms_data: dictionary with two optional keys:
        * 'approvalOfSMS' - boolean informing whether family is accepting SMS messages,
        * 'languageOfSMS' - language code for language in which family will receive messages.
        If parameter is empty, default values are used. False for approval and code for first language
        from sorted core.models.Language.
    :return: newly created FamilySMS object
    :raises ValidationError: if given language code is not specified in tblLanguages or approvalOfSMS is not boolean.
    """
    if family_sms_data is None:
        family_sms_data = get_default_sms_data()

    validate_family_sms_data(family_sms_data)
    family = Family.objects.get(uuid=family_uuid)

    if FamilySMS.objects.filter(family=family, validity_to__isnull=True).exists():
        raise ValidationError(F"FamilySMS for family {family_uuid} already exists")

    family_sms = FamilySMS(family=family,
                           approval_of_sms=family_sms_data.get('approvalOfSMS'),
                           language_of_sms=family_sms_data.get('languageOfSMS')
                           )
    family_sms.save()
    return family_sms


def update_family_sms_policy(family_uuid: str, updated_family_sms_fields: dict = None) -> FamilySMS:
    """
    Update familySMS for given family.
    :param family_uuid: UUID of family for which FamilySMS will be created
    :param updated_family_sms_fields: dictionary with two optional keys:
        * 'approvalOfSMS' - boolean informing whether family is accepting SMS messages,
        * 'languageOfSMS' - language code for language in which family will receive messages.
    :return: updated FamilySMS object
    :raises ValidationError: if given language code is not specified in tblLanguages.
    """
    if not updated_family_sms_fields:
        return None

    family = Family.objects.get(uuid=family_uuid)
    current_family_sms = FamilySMS.objects.filter(family__uuid=family.uuid, validity_to__isnull=True).first()

    if current_family_sms is None:
        logger.warning(F"Update FamilySMS for family {family} has failed, family doesn't have sms policy assigned, "
                       "default one is being created.")
        # create default family SMS policy
        current_family_sms = create_family_sms_policy(family_uuid)

    updated_approval = updated_family_sms_fields.get('approvalOfSMS', None)
    updated_language = updated_family_sms_fields.get('languageOfSMS', None)

    if updated_approval is not None:
        current_family_sms.approval_of_sms = updated_approval
    if updated_language is not None:
        if not Language.objects.filter(code=updated_language).exists():
            raise ValidationError(F"Language code {updated_language} not listed in available language codes")
        else:
            current_family_sms.language_of_sms = updated_language

    current_family_sms.save()
    return current_family_sms


def delete_family_sms(family_uuids: List[str]) -> List[FamilySMS]:
    """
    Delete FamilySMS for given families. FamilySMS is in 1:1 relation with Family, therefore if it's deleted from
    active family, status is reset to default one and not removed completely. If family is deactivated
    (has ValidityTo != null), then validityTo is also set for FamilySMS.
    :param family_uuids: UUIDs of families for which FamilySMS will be deleted
    :return: list of deleted families
    """
    families = Family.objects.filter(uuid__in=family_uuids)
    ids = [x.id for x in families]
    families_sms = FamilySMS.objects.filter(family__id__in=ids)

    deleted = []
    for sms in families_sms:
        if sms.family.validity_to is None:
            default = get_default_sms_data()
            sms.approval_of_sms = default['approvalOfSMS']
            sms.language = default['languageOfSMS']
        else:
            sms.validity_to = datetime.now()
        sms.save()
        deleted.append(sms)
    return deleted
