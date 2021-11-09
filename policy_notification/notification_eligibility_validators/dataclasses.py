from dataclasses import dataclass

from policy.models import Policy
from policy_notification.models import IndicationOfPolicyNotificationsDetails


@dataclass()
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

