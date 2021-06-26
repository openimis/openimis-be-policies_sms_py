from unittest.mock import patch, PropertyMock
from unittest import TestCase

import requests

from policy_notification.notification_gateways import EGASMSGateway
from policy_notification.notification_gateways.RequestBuilders import BaseSMSBuilder


class TestEGASMSGateway(TestCase):
    BUILDER = BaseSMSBuilder()
    MESSAGE_CONTENT = 'Test sms message'
    TEST_PROVIDER_CONFIG = {
        "GateUrl": "http://127.0.0.1:8000",
        "SmsResource": "/api/gateway_endpoint/",
        "PrivateKey": "endpoint_private_key",
        "UserId": "test_user_id",
        "SenderId": "test_sender_id",
        "ServiceId": "test_service_id",
        "RequestType": "api",
        "HeaderKeys": "X-Auth-Request-Hash,X-Auth-Request-Id,X-Auth-Request-Type",
        "HeaderValues": "PrivateKey,UserId,RequestType"
    }

    TEST_MODULE_CONFIG = {
        'providers': {
            'eGASMSGateway': TEST_PROVIDER_CONFIG
        }
    }

    EXPECTED_REQUEST = {
        'url': "http://127.0.0.1:8000/api/gateway_endpoint/",
        'body': MESSAGE_CONTENT,
        'headers': {
            'X-Auth-Request-Hash': 'endpoint_private_key',
            'X-Auth-Request-Id': 'test_user_id',
            'X-Auth-Request-Type': 'api',
            'Content-Length': str(len(MESSAGE_CONTENT))
        }
    }

    def setUp(self):
        self.request_called = None

    def assign_test_output(self, output):
        self.request_called = output

    @patch('policy_notification.apps.PolicyNotificationConfig.providers', new_callable=PropertyMock)
    def test_gateway_send_sms(self, config):
        config.return_value = self.TEST_MODULE_CONFIG['providers']

        gateway = EGASMSGateway(self.BUILDER)
        with patch.object(requests.Session, 'send', side_effect=self.assign_test_output) as mock_method:
            output = gateway.send_notification(self.MESSAGE_CONTENT)
            self._assert_request(self.request_called)
            mock_method.assert_called_once_with(self.request_called)

    def _assert_request(self, request):
        self.assertEqual(request.url, self.EXPECTED_REQUEST['url'])
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.body, self.EXPECTED_REQUEST['body'])
        self.assertDictEqual(dict(request.headers), self.EXPECTED_REQUEST['headers'])
