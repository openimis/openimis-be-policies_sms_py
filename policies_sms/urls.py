from django.urls import path
from . import views

urlpatterns = [
    path('test_messages/', views.test_messages, name='test_text_messages'),
]
