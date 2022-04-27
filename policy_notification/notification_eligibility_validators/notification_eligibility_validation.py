import logging
from datetime import datetime
from typing import Callable, Union, Type

from django.db.models import Prefetch
from django_mysql.models import QuerySet
from policy.models import Policy
from policy_notification.apps import PolicyNotificationConfig
from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from policy_notification.notification_eligibility_validators.abstract_validator import AbstractEligibilityValidator, \
    QuerysetEligibilityValidationMixin
from django.db.models.query_utils import Q

from policy_notification.notification_eligibility_validators.not_eligible_notification_handler import \
    NotEligibleNotificationHandler

logger = logging.getLogger(__name__)


class PolicyNotificationEligibilityValidation(QuerysetEligibilityValidationMixin, AbstractEligibilityValidator):
    NOTIFICATION_NOT_IN_INDICATION_TABLE = "Notification of type {notification} doesn't have representation " \
                                           "in IndicationOfPolicyNotifications table."

    NON_ELIGIBLE_HANDLER: Type[NotEligibleNotificationHandler] = NotEligibleNotificationHandler

    NotificationCollection = 'QuerySet[Policy]'  # Typing

    BASE_VALIDATION_REJECTION_REASON = \
        IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_SENT_NO_PERMISSION_FOR_NOTIFICATIONS

    TYPE_VALIDATION_REJECTION_REASON = \
        IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_PASSED_VALIDATION

    TYPE_VALIDATION_REJECTION_DETAILS = 'Activation on effective day.'

    def __init__(self, notification_collection: NotificationCollection, type_of_notification: str):
        notification_collection = self._prefetch_details_list(notification_collection)
        super().__init__(notification_collection, type_of_notification)

    def _get_validation_for_notification_type(self, notification_type: str):
        if notification_type == 'activation_of_policy':
            return self._validate_activation_of_policy_eligibility
        return None

    def _base_eligibility_validation(self, notification_collection, type_of_notification):
        return self.__base_eligibility(notification_collection, type_of_notification)

    def _handle_not_valid_entries(self):
        handler = self.NON_ELIGIBLE_HANDLER(self.type_of_notification)
        handler.save_information_about_not_eligible_policies(self.invalid_collection)

    def __base_eligibility(self, notification_collection, type_of_notification):
        valid_policies = notification_collection.filter(family__family_notification__approval_of_notification=True)
        if hasattr(IndicationOfPolicyNotifications, type_of_notification):
            # Confirm that for given policy notification was not sent, or was sent with error
            valid_policies = valid_policies.filter(self.__indication_filter(type_of_notification))
        else:
            logger.warning(self.NOTIFICATION_NOT_IN_INDICATION_TABLE.format(type_of_notification))
        return valid_policies

    @classmethod
    def __indication_filter(cls, type_of_notification):
        # Confirm that for given policy notification was not sent, or was sent with error
        indication_not_exit = Q(indication_of_notifications__isnull=True)
        indication_not_sent = cls.__notification_not_sent_filter(type_of_notification)
        indication_failed = cls.__notification_failed_filter(type_of_notification)
        return indication_not_exit | indication_not_sent | indication_failed

    @classmethod
    def __notification_not_sent_filter(cls, type_of_notification):
        return Q(**{f"indication_of_notifications__{type_of_notification}__isnull": True})

    @classmethod
    def __notification_failed_filter(cls, type_of_notification):
        return Q(**{
            f"indication_of_notifications__{type_of_notification}":
                PolicyNotificationConfig.UNSUCCESSFUL_NOTIFICATION_ATTEMPT_DATE
        }) & Q(**{
            f"indication_of_notifications__details__status":
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_SENT_DUE_TO_ERROR,
            f"indication_of_notifications__details__notification_type": type_of_notification
        })

    @classmethod
    def _validate_activation_of_policy_eligibility(cls, policies_collection: NotificationCollection):
        if PolicyNotificationConfig.eligible_notification_types['starting_of_policy']:
            return cls.__check_if_starting_on_same_day(policies_collection)
        else:
            return policies_collection

    @classmethod
    def __check_if_starting_on_same_day(cls, policies_collection: NotificationCollection):
        # If the activation date is equal to the effective date, only the notification regarding starting_of_policy
        # should be sent.
        today = datetime.now().date()
        return policies_collection.filter(~Q(effective_date=today))

    def _prefetch_details_list(self, notification_collection):
        return notification_collection.select_related('indication_of_notifications') \
            .prefetch_related(Prefetch(
            'indication_of_notifications__details',
            queryset=IndicationOfPolicyNotificationsDetails.objects.filter(validity_to__isnull=True),
            to_attr='details_list'
        )).all()
