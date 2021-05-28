from policies_sms.SMSGateway.RequestBuilders.abstract_sms_request_builder import SMSRequestBuilderAbs
from requests import Request, PreparedRequest


class BaseSMSBuilder(SMSRequestBuilderAbs):

    def set_request_authorization(self, authorization, url=''):
        self._sms_request.prepare_auth(authorization, url=url)

    def set_request_headers(self, headers):
        self._sms_request.prepare_headers(headers)

    def set_request_content(self, content):
        self._sms_request.prepare_method(content)

    def set_request_method(self, request_type):
        self._sms_request.prepare_method(request_type)

    def set_request_url(self, url, url_params=None):
        self._sms_request.prepare_url(url, url_params)

    def reset(self):
        req = Request(url=self._default_url, method=self._default_type, data=self._default_data)
        self._sms_request: PreparedRequest = req.prepare()
