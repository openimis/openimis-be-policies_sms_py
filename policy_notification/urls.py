from django.urls import path
from . import views

urlpatterns = [
    path('test_messages/', views.test_messages, name='test_text_messages'),
    path('test_config/', views.test_config, name='test_config'),
    path('test_sms/', views.test_sms, name='test_sms'),
]
