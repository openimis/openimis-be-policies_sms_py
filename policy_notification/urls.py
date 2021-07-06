from django.urls import path
from . import views

urlpatterns = [
    path('communication_by_notification_report/', views.family_policy_notification_report, name='report'),
]
