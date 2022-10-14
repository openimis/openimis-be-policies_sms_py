from django.test import TestCase

from requests import PreparedRequest
from requests.auth import HTTPBasicAuth

from policy_notification.notification_gateways.RequestBuilders import BaseSMSBuilder


class TestRequestBuilder(TestCase):
    TEST_URL = 'http://test_url.test'
    TEST_URL_PARAMS = {'arg1': 'val1', 'arg2': 2}
    TEST_HEADERS = {
        'header1': 'HEADER1'
    }
    TEST_AUTHORIZATION = HTTPBasicAuth('username1', 'password1')
    TEST_BODY = 'Test body of the request'

    EXPECTED_HEADERS_GET = {'header1': 'HEADER1', 'Authorization': 'Basic dXNlcm5hbWUxOnBhc3N3b3JkMQ=='}
    EXPECTED_HEADERS_POST = {'header1': 'HEADER1',
                             'Authorization': 'Basic dXNlcm5hbWUxOnBhc3N3b3JkMQ==',
                             'Content-Length': '24'}
    EXPECTED_GET_URL = 'http://test_url.test/?arg1=val1&arg2=2'
    EXPECTED_POST_URL = 'http://test_url.test/'

    def test_builder_get_request(self):
        builder = BaseSMSBuilder()
        builder.set_request_method('GET')
        builder.set_request_headers(self.TEST_HEADERS)
        builder.set_request_authorization(self.TEST_AUTHORIZATION)
        builder.set_request_url(self.TEST_URL, self.TEST_URL_PARAMS)
        request: PreparedRequest = builder.get_request()

        self.assertEqual(request.url, self.EXPECTED_GET_URL)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.body, None)
        self.assertDictEqual(dict(request.headers), self.EXPECTED_HEADERS_GET)

    def test_builder_post_request(self):
        builder = BaseSMSBuilder()
        builder.set_request_method('POST')
        builder.set_request_headers(self.TEST_HEADERS)
        builder.set_request_authorization(self.TEST_AUTHORIZATION)
        builder.set_request_url(self.TEST_URL)
        builder.set_request_content(self.TEST_BODY)
        request: PreparedRequest = builder.get_request()

        self.assertEqual(request.url, self.EXPECTED_POST_URL)
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.body, self.TEST_BODY)
        self.assertDictEqual(dict(request.headers), self.EXPECTED_HEADERS_POST)
