from unittest.mock import patch, PropertyMock
from unittest import TestCase

import uuid
from insuree.test_helpers import create_test_insuree
from insuree.models import Family
from policies_sms import utils
from policies_sms.services import *


class TestFamilySMSServices(TestCase):
    SMS_APPROVED_DATA = {'approvalOfSMS': True, 'languageOfSMS': 'en'}
    SMS_DECLINED_DATA = {'approvalOfSMS': True, 'languageOfSMS': 'fr'}
    EXPECTED_DEFAULT = {'approvalOfSMS': False, 'languageOfSMS': 'en'}
    SMS_INVALID_LANGUAGE_DATA = {'approvalOfSMS': True, 'languageOfSMS': 'uv'}
    SMS_UPDATE_DATA = {'approvalOfSMS': True, 'languageOfSMS': 'fr'}

    def setUp(self):
        self.test_insuree = create_test_insuree(with_family=True)
        self.test_family = self.test_insuree.family
        self.test_sms = None

    def tearDown(self):
        if self.test_insuree:
            self.test_insuree.delete()
        if self.test_family:
            self.test_family.delete()

    def test_create_approve(self):
        family_sms_entry = create_family_sms_policy(self.test_family.uuid, self.SMS_APPROVED_DATA)

        self.assertEqual(family_sms_entry.family, self.test_family)
        self.assertEqual(family_sms_entry.approval_of_sms, self.SMS_APPROVED_DATA['approvalOfSMS'])
        self.assertEqual(family_sms_entry.language_of_sms, self.SMS_APPROVED_DATA['languageOfSMS'])

    def test_create_decline(self):
        family_sms_entry = create_family_sms_policy(self.test_family.uuid, self.SMS_DECLINED_DATA)

        self.assertEqual(family_sms_entry.family, self.test_family)
        self.assertEqual(family_sms_entry.approval_of_sms, self.SMS_DECLINED_DATA['approvalOfSMS'])
        self.assertEqual(family_sms_entry.language_of_sms, self.SMS_DECLINED_DATA['languageOfSMS'])

    def test_create_default(self):
        family_sms_entry = create_family_sms_policy(self.test_family.uuid)

        self.assertEqual(family_sms_entry.family, self.test_family)
        self.assertEqual(family_sms_entry.approval_of_sms, self.EXPECTED_DEFAULT['approvalOfSMS'])
        self.assertEqual(family_sms_entry.language_of_sms, self.EXPECTED_DEFAULT['languageOfSMS'])

    def test_update_sms_policy(self):
        create_family_sms_policy(self.test_family.uuid)
        updated_sms_entry = update_family_sms_policy(self.test_family.uuid, self.SMS_UPDATE_DATA)

        self.assertEqual(updated_sms_entry.family, self.test_family)
        self.assertEqual(updated_sms_entry.approval_of_sms, self.SMS_UPDATE_DATA['approvalOfSMS'])
        self.assertEqual(updated_sms_entry.language_of_sms, self.SMS_UPDATE_DATA['languageOfSMS'])

    def test_update_non_existing_family(self):
        self.assertRaises(Family.DoesNotExist, update_family_sms_policy, uuid.uuid4(), self.SMS_UPDATE_DATA)

    def test_create_invalid_language(self):
        self.assertRaises(ValidationError, create_family_sms_policy,
                          self.test_family.uuid, self.SMS_INVALID_LANGUAGE_DATA)

    def test_delete_active_family(self):
        expected_values = utils.get_default_sms_data()
        family_sms_entry = create_family_sms_policy(self.test_family.uuid)
        output = delete_family_sms([self.test_family.uuid])
        deleted = output[0]

        self.assertEqual(len(output), 1)
        self.assertEqual(deleted.approval_of_sms, expected_values['approvalOfSMS'])
        self.assertEqual(deleted.language_of_sms, expected_values['languageOfSMS'])
        self.assertEqual(deleted.validity_to, None)  # For active family it's not actually deleted
        self.assertEqual(family_sms_entry.family, deleted.family)

    @patch('insuree.models.Family.validity_to', new_callable=PropertyMock)
    def test_delete_inactive_family(self, validity_to):
        expected_values = utils.get_default_sms_data()
        family_sms_entry = create_family_sms_policy(self.test_family.uuid)

        validity_to.return_value = datetime.now()  # mock family deletion
        output = delete_family_sms([self.test_family.uuid])
        deleted = output[0]

        self.assertEqual(len(output), 1)
        self.assertEqual(deleted.approval_of_sms, expected_values['approvalOfSMS'])
        self.assertEqual(deleted.language_of_sms, expected_values['languageOfSMS'])
        self.assertEqual(family_sms_entry.family, deleted.family)
        self.assertIsNotNone(deleted.validity_to)

