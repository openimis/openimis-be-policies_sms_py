from unittest.mock import patch
from policy.models import Policy

from policy_notification.services import *
from policy_notification.tests.Triggers.base_trigger_test_class import BaseTriggerTestCase


class TestActivePolicyTrigger(BaseTriggerTestCase):

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_activated_policies_new(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_activated_policies()
        self.assertEqual(len(altered_policies), 1)
        self.assertEqual(altered_policies[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_activated_policies_recently_changed(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self._create_policy_history()

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_activated_policies()
        self.assertEqual(len(altered_policies), 1)
        self.assertEqual(altered_policies[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_activated_policies_same_status(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self._create_policy_history(Policy.STATUS_ACTIVE)

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_activated_policies()
        self.assertEqual(len(altered_policies), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_activated_policies_renewed_policy(self, mocked_dt):
        self.policy.stage = Policy.STAGE_RENEWED
        self.policy.save()
        mocked_dt.now.return_value = datetime(2021, 6, 2)

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_activated_policies()
        self.assertEqual(len(altered_policies), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_renewed_policies_new(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self.policy.stage = Policy.STAGE_RENEWED
        self.policy.save()
        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_renewed_policies()
        self.assertEqual(len(altered_policies), 1)
        self.assertEqual(altered_policies[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_renewed_policies_recently_changed(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self._create_policy_history()
        self.history_policy.stage = Policy.STAGE_RENEWED
        self.policy.stage = Policy.STAGE_RENEWED
        self.history_policy.save()
        self.policy.save()

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_renewed_policies()
        self.assertEqual(len(altered_policies), 1)
        self.assertEqual(altered_policies[0], self.policy.id)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_renewed_policies_same_status(self, mocked_dt):
        mocked_dt.now.return_value = datetime(2021, 6, 2)
        self._create_policy_history(Policy.STATUS_ACTIVE)

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_renewed_policies()
        self.assertEqual(len(altered_policies), 0)

    @patch('policy_notification.notification_triggers.notification_triggers.datetime')
    def test_find_renewed_policies_new_policy(self, mocked_dt):
        self.policy.stage = Policy.STATUS_ACTIVE
        self.policy.save()
        mocked_dt.now.return_value = datetime(2021, 6, 2)

        altered_policies = self.TEST_TRIGGER_DETECTOR.find_newly_renewed_policies()
        self.assertEqual(len(altered_policies), 0)
