from datetime import timedelta, date
from unittest.mock import patch

from django.test import TestCase
from policy.test_helpers import create_test_policy
from insuree.test_helpers import create_test_insuree
from insuree.models import InsureePolicy
from product.test_helpers import create_test_product

from policy_notification.models import IndicationOfPolicyNotifications
from policy_notification.notification_dispatcher import NotificationDispatcher
from policy_notification.notification_gateways import TextNotificationProvider, NotificationSendingResult
from policy_notification.notification_templates import DefaultNotificationTemplates
from policy_notification.services import *
from policy_notification.notification_triggers.notification_triggers import NotificationTriggerEventDetectors


class DispatcherTest(TestCase):
    TEST_PROVIDER = TextNotificationProvider
    TEST_TEMPLATES = DefaultNotificationTemplates
    TEST_TRIGGER_DETECTOR = NotificationTriggerEventDetectors

    def setUp(self):
        self.create_policy()

    def tearDown(self):
        InsureePolicy.objects.get(policy=self.policy).delete()
        self.policy.delete()
        self.test_insuree.family = None
        self.test_insuree.save()
        self.test_family.delete()
        self.test_insuree.delete()
        self.test_product.delete()

    def create_policy(self):
        self.test_insuree = create_test_insuree(with_family=True, custom_props={"phone": 123123123})
        self.test_product = create_test_product("PROD1111", custom_props={
            "member_count": 5,
            "administration_period": 0,
            "lump_sum": 0,
            "premium_adult": 300,
            "premium_child": 200,
            "registration_lump_sum": 250,
            "general_assembly_lump_sum": 130,
            "insurance_period": 12,
        })
        self.test_family = self.test_insuree.family
        self.test_family.family_notification = FamilyNotification(approval_of_notification=True, language_of_notification='en')
        self.test_family.family_notification.save()
        self.test_family.save()
        self.policy = create_test_policy(
            product=self.test_product,
            insuree=self.test_insuree,
            custom_props={
             "status": 2,
             "validity_from": datetime(2021, 6, 1, 10),
             "effective_date": date(2019, 1, 1)
        })

        self.test_custom_props = {
            'InsuranceID': self.test_insuree.chf_id,
            'Name': F"{self.test_insuree.other_names} {self.test_insuree.last_name}",
            'EffectiveDate': self.policy.effective_date,
            'ExpiryDate': self.policy.expiry_date,
            'ProductCode': self.policy.product.code,
            'ProductName': self.policy.product.name
        }

    @patch('policy_notification.notification_triggers.NotificationTriggerEventDetectors.find_newly_activated_policies')
    def test_send_notification_for_eligible_policies(self, find_policies):
        find_policies.return_value = [self.policy.id]
        with patch.object(TextNotificationProvider, 'send_notification',
                          return_value=NotificationSendingResult(success=True)) as mock_sent:
            provider = TextNotificationProvider()

            dispatcher = NotificationDispatcher(provider, self.TEST_TEMPLATES(), self.TEST_TRIGGER_DETECTOR())
            dispatcher.send_notification_new_active_policies()

            expected_msg = self.TEST_TEMPLATES().notification_on_activation % self.test_custom_props
            mock_sent.assert_called_once_with(expected_msg, family_number='123123123')
            self.assertIsNotNone(self.policy.indication_of_notifications.activation_of_policy)

    @patch('policy_notification.notification_triggers.NotificationTriggerEventDetectors.find_newly_activated_policies')
    def test_send_notification_for_eligible_policies_already_sent(self, find_policies):
        self.policy.indication_of_notifications = IndicationOfPolicyNotifications()
        self.policy.indication_of_notifications.activation_of_policy = datetime.now()
        self.policy.effective_date = self.policy.effective_date + timedelta(days=1)
        self.policy.indication_of_notifications.save()
        self.policy.save()

        find_policies.return_value = [self.policy.id]
        with patch.object(TextNotificationProvider, 'send_notification', return_value=None) as mock_sent:
            provider = TextNotificationProvider()

            dispatcher = NotificationDispatcher(provider, self.TEST_TEMPLATES(), self.TEST_TRIGGER_DETECTOR())
            dispatcher.send_notification_new_active_policies()
            mock_sent.assert_not_called()

    @patch('policy_notification.notification_triggers.NotificationTriggerEventDetectors.find_newly_activated_policies')
    def test_no_active_notification_for_policy_starting_same_day(self, find_policies):
        find_policies.return_value = [self.policy.id]
        self.policy.effective_date = datetime.now()
        self.policy.save()

        with patch.object(TextNotificationProvider, 'send_notification', return_value=None) as mock_sent:
            provider = TextNotificationProvider()

            dispatcher = NotificationDispatcher(provider, self.TEST_TEMPLATES(), self.TEST_TRIGGER_DETECTOR())
            dispatcher.send_notification_new_active_policies()
            mock_sent.assert_not_called()
