from datetime import datetime
from typing import Callable, Union

from policy_notification.notification_eligibility_validators.abstract_validator import AbstractEligibilityValidator
from django.db.models import QuerySet
from django.db.models.query_utils import Q


class PolicyEligibilityValidation(AbstractEligibilityValidator):
    NotificationCollection = QuerySet

    def get_validation_for_notification_type(self, notification_type: str) \
            -> Union[Callable[[NotificationCollection], NotificationCollection], None]:
        if notification_type == 'activation_of_policy':
            return self._check_if_starting_on_same_day

        return None

    def _check_if_starting_on_same_day(self, policies_collection: NotificationCollection):
        # If the activation date is equal to the effective date, only the notification regarding starting_of_policy
        # should be sent.
        today = datetime.now().date()
        return policies_collection.filter(~Q(effective_date=today))
