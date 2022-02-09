import graphene
from graphene_django import DjangoObjectType
from core import ExtendedConnection
from policy_notification.models import FamilyNotification


class FamilyNotificationGQLType(DjangoObjectType):
    class Meta:
        model = FamilyNotification
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "family__uuid": ["exact"],
            "approval_of_notification": ["exact"],
            "language_of_notification": ["exact"]
        }
        connection_class = ExtendedConnection
