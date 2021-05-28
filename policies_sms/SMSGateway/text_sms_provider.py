import logging
import re

from policies_sms.SMSGateway.abstract_sms_gateway import SMSGatewayAbs
from policies_sms.apps import PoliciesSmsConfig
from os import walk, mkdir, path

logger = logging.getLogger(__name__)


class TextSMSProvider(SMSGatewayAbs):
    """
    Generic sms provider made for test purposes, it doesn't send text messages but save them in local directory
    instead.
    """

    @property
    def provider_configuration_key(self):
        return "TextSMSProvider"

    @property
    def _gateway_provider_configuration(self):
        config = PoliciesSmsConfig.providers.get(self.provider_configuration_key, None)
        if config is None:
            logger.warning("Configuration for TextSMSProvider not found, using default one")
            return {'DestinationFolder': 'sent_sms'}
        else:
            return config

    def send_sms(self, sms_message, filename=None):
        save_dir = self.get_provider_config_param('DestinationFolder')
        if not filename:
            filename = self.__get_next_default_filename(save_dir)

        sms_path = path.join(save_dir, filename)
        print(sms_path)
        with open(sms_path, "w+") as sms_file:
            sms_file.write(sms_message)

    def __get_next_default_filename(self, save_dir):
        # By default smses are saved as SMSMessage_{id}.txt, where id is unique integer
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
        return re.findall('SMSMessage_\d+\.txt', filename) is not None

    def __create_directory_if_not_exists(self, save_dir):
        if path.exists(save_dir):
            return
        else:
            mkdir(save_dir)
