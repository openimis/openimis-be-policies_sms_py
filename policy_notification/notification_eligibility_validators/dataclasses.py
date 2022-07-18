from dataclasses import dataclass
from typing import Callable, Any, Collection

from policy.models import Policy
from policy_notification.models import IndicationOfPolicyNotificationsDetails


@dataclass
class IneligibleObject:
    policy: Policy
    reason: int = 0
    details: str = None

    def to_indication_details(self, type_of_notification) -> IndicationOfPolicyNotificationsDetails:
        return IndicationOfPolicyNotificationsDetails(**{
                'indication_of_notification': self.policy.indication_of_notifications,
                'notification_type': type_of_notification,
                'status':  self.reason,
                'details': self.details
        })


@dataclass
class ValidationDefinition:
    error_type_code: int  # Should align with IndicationOfPolicyNotificationsDetails.SendIndicationStatus
    validation_details: str
    validation_function: Callable[[Collection, str], Collection]
