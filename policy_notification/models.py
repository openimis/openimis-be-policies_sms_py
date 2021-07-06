from django.db import models
from core import models as core_models
from core.utils import get_first_or_default_language
from insuree.models import Family
from policy.models import Policy
from enum import IntEnum


class FamilyNotification(core_models.BaseVersionedModel):
    class FamilyComunicationModes(IntEnum):
        ALL = 0
        FULL_COMMUNICATION_ENABLED_CODE = 1
        APPROVAL_NO_PHONE_NUMBER_CODE = 2
        NO_APPROVAL_PHONE_NUMBER_CODE = 3
        NO_APPROVAL_NO_PHONE_NUMBER_CODE = 4

    # id field is required by Django ORM, however not included in legacy version of model
    family = models.OneToOneField(Family, models.CASCADE, db_column='FamilyID',
                                  related_name="family_notification", primary_key=True)
    approval_of_notification = models.BooleanField(db_column='ApprovalOfSMS', default=False, null=False)
    language_of_notification = models.CharField(db_column='LanguageOfSMS', max_length=5,
                                                default=get_first_or_default_language().code, null=False)

    class Meta:
        managed = False
        db_table = 'tblFamilySMS'


class IndicationOfPolicyNotifications(core_models.BaseVersionedModel):
    # id field is required by Django ORM, however not included in legacy version of model
    policy = models.OneToOneField(Policy, models.CASCADE, db_column='PolicyID',
                                  related_name="indication_of_notifications", primary_key=True)

    activation_of_policy = models.DateTimeField(db_column='NotificationOnActivationSent', null=True)
    starting_of_policy = models.DateTimeField(db_column='NotificationOnEffectiveSent', null=True)
    need_for_renewal = models.DateTimeField(db_column='NotificationBeforeExpirySent', null=True)
    expiration_of_policy = models.DateTimeField(db_column='NotificationOnExpirationSent', null=True)
    reminder_after_expiration = models.DateTimeField(db_column='NotificationAfterExpirationSent', null=True)
    renewal_of_policy = models.DateTimeField(db_column='NotificationOnRenewalSent', null=True)

    class Meta:
        db_table = 'tblIndicationOfPolicyNotifications'