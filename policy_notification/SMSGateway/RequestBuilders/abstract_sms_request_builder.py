from abc import ABC


class SMSRequestBuilderAbs(ABC):

    def __init__(self, default_type='GET', default_data='', default_url='http://127.0.0.1'):
        self._sms_request = None
        self._default_type = default_type
        self._default_data = default_data
        self._default_url = default_url
        self.reset()

    def get_request(self):
        return self._sms_request

    def set_request_authorization(self, authorization, url=''):
        raise NotImplementedError("add_request_authorization not implemented")

    def set_request_headers(self, headers):
        raise NotImplementedError("add_request_headers not implemented")

    def set_request_content(self, content, files=None, json=None):
        raise NotImplementedError("set_request_content not implemented")

    def set_request_method(self, request_type):
        raise NotImplementedError("set_request_type not implemented")

    def set_request_url(self, url, url_params=None):
        raise NotImplementedError("set_request_url not implemented")

    def reset(self):
        raise NotImplementedError("reset not implemented")
