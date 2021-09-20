import logging
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import IndicationOfPolicyNotifications
from .notification_eligibility_validators import PolicyEligibilityValidation
from .notification_gateways.abstract_sms_gateway import NotificationGatewayAbs
from .notification_templates import DefaultNotificationTemplates
from policy_notification.notification_triggers import NotificationTriggerEventDetectors
from .notification_triggers import NotificationTriggerAbs
from .notification_client import PolicyNotificationClient
from policy.models import Policy, PolicyRenewal

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    NOTIFICATION_NOT_IN_INDICATION_TABLE = "Notification of type {notification} doesn't have representation " \
                                           "in IndicationOfPolicyNotifications table."

    def __init__(self, notification_provider: NotificationGatewayAbs,
                 notification_templates_source: DefaultNotificationTemplates = DefaultNotificationTemplates,
                 trigger_detector: NotificationTriggerAbs = NotificationTriggerEventDetectors,
                 eligibility_validation: PolicyEligibilityValidation = PolicyEligibilityValidation()):
        self.notification_client = PolicyNotificationClient(notification_provider=notification_provider)
        self.templates = notification_templates_source
        self.trigger_detector = trigger_detector
        self.eligibility_validation = eligibility_validation

    def send_notification_new_active_policies(self):
        policies = self.trigger_detector.find_newly_activated_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_on_activation, 'activation_of_policy')

    def send_notification_starting_of_policy(self):
        policies = self.trigger_detector.find_newly_effective_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_on_effective, 'starting_of_policy')

    def send_notification_new_renewed_policies(self):
        policies = self.trigger_detector.find_newly_renewed_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_on_renewal, 'renewal_of_policy')

    def send_notification_not_renewed_soon_expiring_policies(self):
        policies = self.trigger_detector.find_soon_expiring_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_before_expiry, 'expiration_of_policy')

    def send_notification_not_renewed_expired_policies(self):
        policies = self.trigger_detector.find_recently_expired_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_after_expiry, 'reminder_after_expiration')

    def send_notification_expiring_today_policies(self):
        policies = self.trigger_detector.find_expiring_today_policies()
        self._send_notification_for_eligible_policies(
            policies, self.templates.notification_on_expiration, 'expiration_of_policy')

    def _policy_customs(self, policy: Policy):
        """
        Build dictionary of parameters which will be used as custom parameters in notification templates.
        :param policy: Policy for which notification will be sent
        :return: Dictionary which keys used in templates
        """
        head = policy.family.head_insuree
        customs = {
            'InsuranceID': head.chf_id,
            'Name': F"{head.other_names} {head.last_name}",
            'EffectiveDate': policy.effective_date,
            'ExpiryDate': policy.expiry_date,
            'ProductCode': policy.product.code,
            'ProductName': policy.product.name
        }
        return customs

    def _send_notification_for_eligible_policies(self, policies, notification_template, type_of_notification):
        notification_eligible_policies = self._get_eligible_policies(policies, type_of_notification)
        notification_sent_successfully = []
        for policy in notification_eligible_policies:
            result = self._send_notification(policy, notification_template)
            if result:
                notification_sent_successfully.append(policy)
            try:
                indication = policy.indication_of_notifications
            except ObjectDoesNotExist:
                indication = IndicationOfPolicyNotifications(policy=policy)

            if not hasattr(indication, type_of_notification):
                logger.warning(self.NOTIFICATION_NOT_IN_INDICATION_TABLE.format(type_of_notification))
            else:
                if result:
                    setattr(indication, type_of_notification, datetime.now())
                    indication.save()
        return notification_sent_successfully

    def _send_notification(self, policy, notification_template):
        custom = self._policy_customs(policy)
        return self.notification_client.send_notification_from_template(policy, notification_template, custom)

    def _get_eligible_policies(self, policies_ids, type_of_notification):
        policies = Policy.objects \
            .filter(id__in=policies_ids) \
            .filter(family__family_notification__approval_of_notification=True)

        base_eligibility = self.__base_eligibility(policies, type_of_notification)
        additional_eligibility = self.__additional_eligibility(base_eligibility, type_of_notification)
        return additional_eligibility

    def __base_eligibility(self, policies, type_of_notification):
        if hasattr(IndicationOfPolicyNotifications, type_of_notification):
            # Confirm that for given policy notification was not sent
            indication_filter = {
                f"indication_of_notifications__{type_of_notification}__isnull": True,
            }
            indication_filter = Q(indication_of_notifications__isnull=True) | Q(**indication_filter)
            policies = policies.filter(indication_filter)
        else:
            logger.warning(self.NOTIFICATION_NOT_IN_INDICATION_TABLE.format(type_of_notification))
        return policies

    def __additional_eligibility(self, policies, type_of_notification):
        return self.eligibility_validation.validate_eligibility(policies, type_of_notification)
