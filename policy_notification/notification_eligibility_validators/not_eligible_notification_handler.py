from policy_notification.apps import PolicyNotificationConfig
from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from django.db.models import Q


class NotEligibleNotificationHandler:
    INDICATION_STATUS = IndicationOfPolicyNotificationsDetails.SendIndicationStatus

    def save_information_about_not_eligible_policies(self, policies, type_of_notification):
        policies = self._filter_out_sent_notifications(policies, type_of_notification)
        self._ensure_indication_exits(policies, type_of_notification)
        self._create_or_override_indication_details(policies, type_of_notification)

    @classmethod
    def _filter_out_sent_notifications(cls, policies, type_of_notifications):
        # Notification is considered as sent if there's date in indication of notification that's different from
        # null (notification not sent) or UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE (flag for sending error)
        not_sent = Q(**{f'indication_of_notifications__{type_of_notifications}': None})
        failed_attempt = Q(**{
            f'indication_of_notifications__{type_of_notifications}':
                PolicyNotificationConfig.UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE
        })

        return policies.filter(not_sent | failed_attempt)

    def _create_or_override_indication_details(self, policies, type_of_notification):
        with_indication_details = policies.filter(
            indication_of_notifications__details__notification_type=type_of_notification
        )
        without_indication_details = policies.exclude(
            id__in=with_indication_details.values('id')
        )

        self.__create_indication_details(without_indication_details, type_of_notification)
        self.__update_indication_details(with_indication_details, type_of_notification)

    def __create_indication_details(self, notifications, type_of_notification):
        IndicationOfPolicyNotificationsDetails.objects.bulk_create(
            IndicationOfPolicyNotificationsDetails(**{
                'indication_of_notification': policy.indication_of_notifications,
                'notification_type': type_of_notification,
                # Values added as annotation during validation
                'status':  policy.rejection_reason,
                'details': policy.rejection_details
            }) for policy in notifications
        )

    def __update_indication_details(self, notifications, type_of_notification):
        for_update = []
        for policy in notifications:
            indication_details = policy.indication_of_notifications.details \
                .get(validity_to=None, notification_type=type_of_notification)
            indication_details.status = policy.rejection_reason
            indication_details.details = policy.rejection_details or ''  # MSQQL Backend doesn't allow None update
            for_update.append(indication_details)
        IndicationOfPolicyNotificationsDetails.objects.bulk_update(for_update, ['status', 'details'])

    def _ensure_indication_exits(self, policies, type_of_notification):
        without_indication = policies.exclude(indication_of_notifications__isnull=False)
        # Create indication for entries without ones
        IndicationOfPolicyNotifications.objects.bulk_create(
            IndicationOfPolicyNotifications(**{
                type_of_notification: PolicyNotificationConfig.UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE,
                'policy': policy,
            }) for policy in without_indication.iterator()
        )
