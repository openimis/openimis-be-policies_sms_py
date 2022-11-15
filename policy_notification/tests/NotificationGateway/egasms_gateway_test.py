import json
from datetime import datetime
from unittest.mock import patch, PropertyMock
from django.test import TestCase

import requests

from policy_notification.notification_gateways import EGASMSGateway
from policy_notification.notification_gateways.RequestBuilders import BaseSMSBuilder


class TestEGASMSGateway(TestCase):
    BUILDER = BaseSMSBuilder()
    MOCKED_SENDING_TIME_UTC_NOW = datetime(2021, 7, 13, 8, 16, 34)

    MESSAGE_CONTENT = json.dumps({
        'data': json.dumps({
            'message': 'test',
            'datetime': '2021-07-13 11:16:34',
            'sender_id': 'sender_id',
            'mobile_service_id': 'service_id',
            'recipients': '1'
        }, separators=(',', ':')),
        'datetime': "2021-07-13 11:16:34"
    }, separators=(',', ':'))

    TEST_PROVIDER_CONFIG = {
        "GateUrl": "http://127.0.0.1:8000",
        "SmsResource": "/api/gateway_endpoint/",
        "PrivateKey": "private_key",
        "UserId": "test_user_id",
        "SenderId": "sender_id",
        "ServiceId": "service_id",
        "RequestType": "api",
        "HeaderKeys": "X-Auth-Request-Hash,X-Auth-Request-Id,X-Auth-Request-Type",
        "HeaderValues": "HashMessage1,UserId,RequestType"
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
            'X-Auth-Request-Hash': 'lI/b3Yz3uIByNpQy+D2xcfBK5I9uoPUAE/sqtw1COxw=',
            'X-Auth-Request-Id': 'test_user_id',
            'X-Auth-Request-Type': 'api',
            'Content-Length': str(len(MESSAGE_CONTENT)),
            'content-type': 'application/json'
        }
    }

    def setUp(self):
        super(TestEGASMSGateway, self).setUp()
        self.maxDiff = None
        self.request_called = None

    def assign_test_output(self, output):
        self.request_called = output

    @patch('policy_notification.apps.PolicyNotificationConfig.providers', new_callable=PropertyMock)
    @patch('policy_notification.notification_gateways.eGASMSGateway.datetime.datetime')
    def test_gateway_send_sms(self, mocked_dt, config):
        config.return_value = self.TEST_MODULE_CONFIG['providers']
        mocked_dt.now.return_value = self.MOCKED_SENDING_TIME_UTC_NOW
        gateway = EGASMSGateway(self.BUILDER)
        with patch.object(requests.Session, 'send', side_effect=self.assign_test_output) as mock_method:
            output = gateway.send_notification('test', family_number="1")
            self._assert_request(self.request_called)
            mock_method.assert_called_once_with(self.request_called)

    def _assert_request(self, request):
        self.assertEqual(request.url, self.EXPECTED_REQUEST['url'])
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.body, self.EXPECTED_REQUEST['body'])
        self.assertDictEqual(dict(request.headers), self.EXPECTED_REQUEST['headers'])
