import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from policy_notification.NotificationTemplates import DefaultSMSTemplates
from policy_notification.apps import PolicyNotificationConfig

from django.utils import translation


def test_messages(request):
    '''
    Endpoint created for testing sms template content and translations from endpoint.
    GET querystring can contain two parameters: 'language' with language code to determine which translation should
    be used (en by default) and 'message' to select specific message (all sms templates are passed by default).
    '''
    lang = request.GET.get("language", "en")
    translation.activate(lang)

    message_name = request.GET.get("message", None)
    messages = DefaultSMSTemplates().get_all()

    if message_name:
        message = messages.get(message_name, None)
        if not message:
            resp_content = {
                'success': False,
                'error_message': F'Getting message {message_name} failed, available messages are:\n'
                                 F' {list((messages.keys()))}'
            }
        else:
            custom_fields = request.GET.get("values", None)
            if custom_fields:
                pairs = map(lambda x: x.split(":"), custom_fields.split(","))
                custom = {k: v for k, v in pairs}
                message = message % custom
            resp_content = {
                'success': True,
                'message': message
            }
    else:
        resp_content = {
            'success': True,
            'messages': messages
        }

    response = HttpResponse(content=json.dumps(resp_content), status=200)
    return response


def test_config(request):
    config = request.GET.get("config", None)
    content = getattr(PolicyNotificationConfig, config) if config else PolicyNotificationConfig.providers

    resp_content = {
        'success': True,
        'config': content
    }

    response = HttpResponse(content=json.dumps(resp_content), status=200)
    return response


@csrf_exempt
def test_sms(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode) if body_unicode else {'content': {}}
    content = body['content']
    content['headers'] = dict(request.headers)

    response = HttpResponse(content=json.dumps(content), status=200)
    return response
