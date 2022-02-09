from concurrent.futures import ThreadPoolExecutor, wait
from itertools import chain
from typing import Iterable

from policy_notification.apps import PolicyNotificationConfig
from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from policy_notification.notification_eligibility_validators.dataclasses import IneligibleObject


class NotEligibleNotificationHandler:
    INDICATION_STATUS = IndicationOfPolicyNotificationsDetails.SendIndicationStatus

    def __init__(self, type_of_notification):
        self.type_of_notification = type_of_notification

    def save_information_about_not_eligible_policies(self, ineligible: Iterable[IneligibleObject]):
        new_ineligible = self._filter_out_sent_notifications(ineligible)
        self._ensure_indication_exits(new_ineligible)
        self._create_or_override_indication_details(new_ineligible)

    def _filter_out_sent_notifications(self, ineligible: Iterable[IneligibleObject]):
        return [
            next_ for next_ in ineligible
            if self.__get_indication_status(next_.policy) in
            (None, PolicyNotificationConfig.UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE)
        ]

    def _create_or_override_indication_details(self, ineligible: Iterable[IneligibleObject]):
        with_details, without_details = self._split_ineligible_by_details(ineligible)
        self.__update_indication_details(with_details)
        self.__create_indication_details(without_details)

    def __create_indication_details(self, ineligible: Iterable[IneligibleObject]):
        details = [
            ineligible_policy.to_indication_details(self.type_of_notification) for ineligible_policy in ineligible
        ]
        IndicationOfPolicyNotificationsDetails.objects.bulk_create(details)

    def __update_indication_details(self, ineligible: Iterable[IneligibleObject]):
        for_update = []
        for ineligible_policy in ineligible:
            details = self.__get_indication_details(ineligible_policy.policy)
            update = ineligible_policy.to_indication_details(self.type_of_notification)
            details.status = update.status
            details.details = update.details or ''  # MSSQL Backend doesn't allow None update
            for_update.append(details)
        IndicationOfPolicyNotificationsDetails.objects.bulk_update(for_update, ['status', 'details'])

    def __get_indication_details(self, policy):
        return policy \
            .indication_of_notifications \
            .details. \
            get(validity_to=None, notification_type=self.type_of_notification)

    def _ensure_indication_exits(self, ineligible: Iterable[IneligibleObject]):
        # Create indication for entries without ones
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [
                executor.submit(self.__create_failed_indication, ineligible_policy.policy)
                for ineligible_policy in ineligible
                if not hasattr(ineligible_policy.policy, 'indication_of_notifications')
            ]
            wait(futures)
            IndicationOfPolicyNotifications.objects.bulk_create(chain(f.result() for f in futures))

    def __create_failed_indication(self, policy):
        return IndicationOfPolicyNotifications(**{
            self.type_of_notification: PolicyNotificationConfig.UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE,
            'policy': policy,
        })

    def __get_indication_status(self, policy):
        # Notification is considered as sent if there's date in indication of notification that's different from
        # null (notification not sent) or UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE (flag for sending error)
        if not hasattr(policy, 'indication_of_notifications'):
            return None
        else:
            indication_status = getattr(policy.indication_of_notifications, self.type_of_notification, None)
            return indication_status

    def _split_ineligible_by_details(self, ineligible):
        def __indication_exists(policy):
            details = policy.indication_of_notifications.details
            return details.filter(notification_type=self.type_of_notification).exists()

        with_, without = [], []
        for next_ in ineligible:
            with_.append(next_) if __indication_exists(next_.policy) else without.append(next_)
        return with_, without
