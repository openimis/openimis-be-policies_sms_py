from datetime import date
from unittest.mock import patch

from policy_notification.services import *
from policy_notification.notification_triggers.notification_triggers import NotificationTriggerEventDetectors
from policy_notification.tests.Triggers.base_trigger_test_class import BaseTriggerTestCase


class TestNoRenewalPolicyTrigger(BaseTriggerTestCase):
    # Renewal reminder before expiry
    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_policies_new(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self.policy.expiry_date = datetime(2021, 6, 7)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_soon_expiring_policies()
        self.assertEqual(len(effective_from_today), 1)
        self.assertEqual(effective_from_today[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_policies_with_renewal(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self.policy.expiry_date = datetime(2021, 6, 7)
        self.policy.save()
        self._create_policy_renewal(self.policy.expiry_date)

        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_soon_expiring_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_policies_new_future(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self.policy.expiry_date = datetime(2021, 6, 8)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_soon_expiring_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_policies_new_past(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self.policy.expiry_date = datetime(2021, 6, 6)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_soon_expiring_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_second_call_in_given_day(self, mocked_dt):
        self.TEST_TRIGGER_DETECTOR.TIME_INTERVAL_HOURS = 8
        try:
            mocked_dt.now.return_value = datetime(2021, 6, 2, 16)
            mocked_dt.today.return_value = date(2021, 6, 2)
            self.policy.expiry_date = datetime(2021, 6, 7)
            self.policy.save()
            effective_from_today = self.TEST_TRIGGER_DETECTOR.find_soon_expiring_policies()
            self.assertEqual(len(effective_from_today), 0)
        finally:
            # Restore previous value
            NotificationTriggerEventDetectors.TIME_INTERVAL_HOURS = 24

    # Renewal reminder before expiry
    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_after_expiry_policies_new(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 1)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_recently_expired_policies()
        self.assertEqual(len(effective_from_today), 1)
        self.assertEqual(effective_from_today[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_after_expiry_policies_with_renewal(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 1)
        self.policy.save()
        self._create_policy_renewal(self.policy.expiry_date)

        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_recently_expired_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_after_expiry_policies_new_future(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 3)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_recently_expired_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_after_expiry_policies_new_past(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 8)
        self.policy.expiry_date = datetime(2021, 6, 1)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_recently_expired_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_after_expiry_second_call_in_given_day(self, mocked_dt):
        self.TEST_TRIGGER_DETECTOR.TIME_INTERVAL_HOURS = 8
        try:
            mocked_dt.now.return_value = datetime(2021, 6, 2, 16)
            mocked_dt.today.return_value = date(2021, 6, 6)
            self.policy.expiry_date = datetime(2021, 6, 1)
            self.policy.save()
            effective_from_today = self.TEST_TRIGGER_DETECTOR.find_recently_expired_policies()
            self.assertEqual(len(effective_from_today), 0)
        finally:
            # Restore previous value
            NotificationTriggerEventDetectors.TIME_INTERVAL_HOURS = 24

    # Expiring today without renewal
    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_expiring_today_policies_new(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 6)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_expiring_today_policies()
        self.assertEqual(len(effective_from_today), 1)
        self.assertEqual(effective_from_today[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_expiring_today_policies_with_renewal(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 6)
        self.policy.save()
        self._create_policy_renewal(self.policy.expiry_date)

        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_expiring_today_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_expiring_today_policies_new_future(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 7)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_expiring_today_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_expiring_today_policies_new_past(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 6)
        self.policy.expiry_date = datetime(2021, 6, 5)
        self.policy.save()
        effective_from_today = self.TEST_TRIGGER_DETECTOR.find_expiring_today_policies()
        self.assertEqual(len(effective_from_today), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_no_renewal_expiring_today_second_call_in_given_day(self, mocked_dt):
        self.TEST_TRIGGER_DETECTOR.TIME_INTERVAL_HOURS = 8
        try:
            mocked_dt.now.return_value = datetime(2021, 6, 2, 16)
            mocked_dt.today.return_value = date(2021, 6, 6)
            self.policy.expiry_date = datetime(2021, 6, 6)
            self.policy.save()
            effective_from_today = self.TEST_TRIGGER_DETECTOR.find_expiring_today_policies()
            self.assertEqual(len(effective_from_today), 0)
        finally:
            # Restore previous value
            NotificationTriggerEventDetectors.TIME_INTERVAL_HOURS = 24
