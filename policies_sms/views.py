import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from policies_sms.SMSTemplates import DefaultSMSTemplates
from django.utils.translation import ugettext, gettext as _
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
