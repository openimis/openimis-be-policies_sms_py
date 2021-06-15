import graphene
from graphene_django import DjangoObjectType
from core import ExtendedConnection
from policies_sms.models import FamilySMS


class FamilySmsGQLType(DjangoObjectType):
    class Meta:
        model = FamilySMS
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "family__uuid": ["exact"],
            "approval_of_sms": ["exact"],
            "language_of_sms": ["exact"]
        }
        connection_class = ExtendedConnection
