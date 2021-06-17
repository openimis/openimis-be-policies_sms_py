import graphene
from graphene_django import DjangoObjectType
from core import ExtendedConnection
from policy_notification.models import FamilySMS


class FamilyNotificationGQLType(DjangoObjectType):
    class Meta:
        model = FamilySMS
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "family__uuid": ["exact"],
            "approval_of_notification": ["exact"],
            "language_of_notification": ["exact"]
        }
        connection_class = ExtendedConnection
