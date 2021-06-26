from django.db import models
from core import models as core_models
from core.utils import get_first_or_default_language
from insuree.models import Family


class FamilySMS(core_models.BaseVersionedModel):
    # id field is required by Django ORM, however not included in legacy version of model
    family = models.OneToOneField(Family, models.CASCADE, db_column='FamilyID',
                                  related_name="familyId", primary_key=True)
    approval_of_notification = models.BooleanField(db_column='ApprovalOfSMS', default=False, null=False)
    language_of_notification = models.CharField(db_column='LanguageOfSMS', max_length=5,
                                       default=get_first_or_default_language().code, null=False)

    class Meta:
        managed = False
        db_table = 'tblFamilySMS'