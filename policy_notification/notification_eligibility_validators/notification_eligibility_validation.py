import logging
from datetime import datetime, timedelta
from typing import Type

from django.db.models import Prefetch
from policy_notification.apps import PolicyNotificationConfig
from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from policy_notification.notification_eligibility_validators.abstract_validator import AbstractEligibilityValidator, \
    QuerysetEligibilityValidationMixin
from django.db.models.query_utils import Q

from policy_notification.notification_eligibility_validators.dataclasses import IneligibleObject, ValidationDefinition
from policy_notification.notification_eligibility_validators.not_eligible_notification_handler import \
    NotEligibleNotificationHandler
from policy_notification.utils import get_notification_indication_filter

logger = logging.getLogger(__name__)


class PolicyNotificationEligibilityValidation(QuerysetEligibilityValidationMixin, AbstractEligibilityValidator):
    NOTIFICATION_NOT_IN_INDICATION_TABLE = "Notification of type {notification} doesn't have representation " \
                                           "in IndicationOfPolicyNotifications table."
    NON_ELIGIBLE_HANDLER: Type[NotEligibleNotificationHandler] = NotEligibleNotificationHandler
    NotificationCollection = 'QuerySet[Policy]'  # Typing

    @property
    def registered_validations(self):
        return [
            ValidationDefinition(
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_SENT_NO_PERMISSION_FOR_NOTIFICATIONS,
                'Rejected due to family denied notifications.',
                self._family_validation),
            ValidationDefinition(
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_PASSED_VALIDATION,
                F'Rejected because type of notification of type `{self.type_of_notification}`'
                F' was sent or is not permitted.',
                self._notification_type_validation
            ),
            ValidationDefinition(
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_PASSED_VALIDATION,
                'Policy is being activated on day of policy start, only start of policy notification is sent.',
                self._validate_activate_on_effective_date),
            ValidationDefinition(
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_SENT_NOTIFICATION_FOR_OBSOLETE_EVENT,
                'Notification attempt for an event after the time when notification is considered relevant.',
                self._validate_policy_activation_date),
            ValidationDefinition(
                IndicationOfPolicyNotificationsDetails.SendIndicationStatus.NOT_SENT_NOTIFICATION_FOR_OBSOLETE_EVENT,
                'Notification attempt for an event after the time when notification is considered relevant.',
                self._validate_policy_renewal_date),
        ]

    def __init__(self, notification_collection: NotificationCollection, type_of_notification: str):
        notification_collection = self._prefetch_details_list(notification_collection)
        super().__init__(notification_collection, type_of_notification)

    def _create_ineligible(self, ineligible, validation_definition):
        return IneligibleObject(
            policy=ineligible, reason=validation_definition.error_type_code,
            details=validation_definition.validation_details
        )

    @classmethod
    def _validate_activate_on_effective_date(cls, notification_collection, notification_type):
        """
        If policy is activated on the effective date and start date notification is enabled only one notification
        is sent.
        """
        if notification_type == 'activation_of_policy' and \
                PolicyNotificationConfig.eligible_notification_types['starting_of_policy']:
            return cls.__check_if_starting_on_same_day(notification_collection)
        else:
            return notification_collection

    def _handle_not_valid_entries(self):
        handler = self.NON_ELIGIBLE_HANDLER(self.type_of_notification)
        handler.save_information_about_not_eligible_policies(self.invalid_collection)

    def _prefetch_details_list(self, notification_collection):
        return notification_collection.select_related('indication_of_notifications') \
            .prefetch_related(Prefetch(
                'indication_of_notifications__details',
                queryset=IndicationOfPolicyNotificationsDetails.objects.filter(validity_to__isnull=True),
                to_attr='details_list')
        ).all()

    @classmethod
    def __check_if_starting_on_same_day(cls, policies_collection: NotificationCollection):
        # If the activation date is equal to the effective date, only the notification regarding starting_of_policy
        # should be sent.
        today = datetime.now().date()
        return policies_collection.filter(~Q(effective_date=today))

    @classmethod
    def _family_validation(cls, notification_collection, type_of_notification):
        validation = notification_collection
        return validation.filter(family__family_notification__approval_of_notification=True).all()

    @classmethod
    def _notification_type_validation(cls, notification_collection, type_of_notification):
        valid_policies = notification_collection
        if hasattr(IndicationOfPolicyNotifications, type_of_notification):
            # Confirm that for given policy notification was not sent, or was sent with error
            valid_policies = valid_policies.filter(cls.__indication_filter(type_of_notification))
        else:
            logger.warning(cls.NOTIFICATION_NOT_IN_INDICATION_TABLE.format(type_of_notification))
        return valid_policies

    @classmethod
    def _validate_policy_activation_date(cls, notification_collection, type_of_notification):
        date_from = datetime.today() - timedelta(
            days=PolicyNotificationConfig.policy_activation_relevance_maximum_days_timedelta)
        if type_of_notification == 'activation_of_policy':
            return notification_collection.filter(validity_from__gte=date_from)
        else:
            return notification_collection

    @classmethod
    def _validate_policy_renewal_date(cls, notification_collection, type_of_notification):
        date_from = datetime.today() - timedelta(
            days=PolicyNotificationConfig.policy_renewal_relevance_maximum_days_timedelta)
        if type_of_notification == 'renewal_of_policy':
            return notification_collection.filter(validity_from__gte=date_from)
        else:
            return notification_collection

    @classmethod
    def __indication_filter(cls, type_of_notification):
        return get_notification_indication_filter(type_of_notification)
