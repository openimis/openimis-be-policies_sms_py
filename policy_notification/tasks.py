from celery import shared_task
from datetime import datetime

import logging

from .apps import PolicyNotificationConfig
from .notification_dispatcher import NotificationDispatcher
from .notification_templates import DefaultNotificationTemplates
from policy_notification.notification_triggers.notification_triggers import NotificationTriggerEventDetectors
from .utils import get_notification_providers


@shared_task
def send_notification_messages():
    logger = logging.getLogger(__name__)
    try:
        notification_providers = get_notification_providers()
        logger.info(F"send_notification_messages task called at {datetime.now()}")
        eligible_notification_types = PolicyNotificationConfig.eligible_notification_types

        event_detector = NotificationTriggerEventDetectors()
        # Ensure time intervals are loaded properly
        event_detector.assign_default_intervals()

        for provider in notification_providers:
            # Scheduled task run at least once per day
            # All gateways are used to inform insurees
            dispatcher = NotificationDispatcher(
                notification_provider=provider(),
                notification_templates_source=DefaultNotificationTemplates(),
                trigger_detector=event_detector,
            )

            if eligible_notification_types.get('activation_of_policy', False):
                dispatcher.send_notification_new_active_policies()

            if eligible_notification_types.get('starting_of_policy', False):
                dispatcher.send_notification_starting_of_policy()

            if eligible_notification_types.get('need_for_renewal', False):
                dispatcher.send_notification_not_renewed_soon_expiring_policies()

            if eligible_notification_types.get('expiration_of_policy', False):
                dispatcher.send_notification_expiring_today_policies()

            if eligible_notification_types.get('reminder_after_expiration', False):
                dispatcher.send_notification_not_renewed_expired_policies()

            if eligible_notification_types.get('renewal_of_policy', False):
                dispatcher.send_notification_new_renewed_policies()
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(F"Failed to execute notification sending, error: {traceback.format_exc()}")
