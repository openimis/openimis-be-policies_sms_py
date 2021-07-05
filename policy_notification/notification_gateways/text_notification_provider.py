import logging
import re

from policy_notification.notification_gateways.abstract_sms_gateway import NotificationGatewayAbs, \
    NotificationSendingResult
from policy_notification.apps import PolicyNotificationConfig
from os import walk, mkdir, path

logger = logging.getLogger(__name__)


class TextNotificationProvider(NotificationGatewayAbs):
    """
    Generic sms provider made for test purposes, it doesn't send text messages but save them in local directory
    instead.
    """

    @property
    def provider_configuration_key(self):
        return "TextNotificationProvider"

    @property
    def _gateway_provider_configuration(self):
        config = PolicyNotificationConfig.providers.get(self.provider_configuration_key, None)
        if config is None:
            logger.warning("Configuration for TextNotificationProvider not found, using default one")
            return {'DestinationFolder': 'sent_notification'}
        else:
            return config

    def send_notification(self, notification_content, family_number=None, filename=None) -> NotificationSendingResult:
        save_dir = self.get_provider_config_param('DestinationFolder')
        if not filename:
            filename = self.__get_next_default_filename(save_dir)

        sms_path = path.join(save_dir, filename)
        with open(sms_path, "w+") as sms_file:
            sms_file.write(notification_content)
        return NotificationSendingResult(sms_path)

    def __get_next_default_filename(self, save_dir):
        # By default sms is saved in SMSMessage_{id}.txt file, where id is unique integer
        # in scope of DestinationFolder
        _, _, filenames = next(walk(save_dir), (None, None, None))

        if not filenames:
            self.__create_directory_if_not_exists(save_dir)
            index = 1
        else:
            all_indexes = [
                self.__get_index_from_filename(sms_file) for sms_file in filenames
                if self.__is_default_filename(sms_file)
            ]
            index = max(all_indexes, default=0) + 1

        return f"SMSMessage_{index}.txt"

    def __get_index_from_filename(self, filename):
        return int(re.findall('\d+', filename)[-1])

    def __is_default_filename(self, filename):
        return re.findall('NotificationMessage_\d+\.txt', filename) is not None

    def __create_directory_if_not_exists(self, save_dir):
        if path.exists(save_dir):
            return
        else:
            mkdir(save_dir)
