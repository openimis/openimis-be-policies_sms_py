import logging

import graphene
from core.schema import signal_mutation_module_after_mutating
from insuree.models import Family, Insuree
from graphene_django.filter import DjangoFilterConnectionField

from policy_notification.gql_queries import FamilySmsGQLType
from policy_notification.services import update_family_sms_policy, create_family_sms_policy, delete_family_sms

logger = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    family_sms = DjangoFilterConnectionField(FamilySmsGQLType)


def on_family_create_mutation(mutation_args):
    head_of_family_chf = mutation_args['data'].get('head_insuree', {}).get('chf_id', None)
    try:
        head_of_family = Insuree.objects.get(chf_id=head_of_family_chf)
        family_uuid = Family.objects.get(head_insuree=head_of_family, validity_to__isnull=True).uuid
        if not family_uuid:
            return []
    except (Family.DoesNotExist, Insuree.DoesNotExist) as e:
        logger.warning(F"Family with head insuree with chf {head_of_family_chf} not found, FamilySMS was not created")
    except Exception as e:
        import traceback
        logger.error("Error ocurred during creating new familySMS, traceback: ")
        traceback.print_exc()

    family_sms_policy = mutation_args['data'].get('contribution', {}).get('PolicyNotification', {})
    create_family_sms_policy(family_uuid, family_sms_policy)
    return []


def on_family_update_mutation(mutation_args):
    family_uuid = mutation_args['data'].get('uuid', None)
    family_sms_policy_update = mutation_args['data'].get('contribution', {}).get('PolicyNotification', {})

    if not family_uuid:
        return []

    if not family_sms_policy_update:
        logger.warning(F"FamilySMS is being updated but contribution.policySms is empty, "
                       F"content of contribution field:\n {mutation_args['data'].get('contribution', {})}.")
        return []

    update_family_sms_policy(family_uuid, family_sms_policy_update)


def on_families_delete_mutation(mutation_args):
    family_uuids = mutation_args['data'].get('uuids', None)

    if not family_uuids:
        return []

    delete_family_sms(family_uuids)


def after_family_mutation(sender, **kwargs):
    return {
        "CreateFamilyMutation": lambda x: on_family_create_mutation(x),
        "UpdateFamilyMutation": lambda x: on_family_update_mutation(x),
        "DeleteFamiliesMutation": lambda x: on_families_delete_mutation(x),
    }.get(sender._mutation_class, lambda x: [])(kwargs)


def bind_signals():
    signal_mutation_module_after_mutating["insuree"].connect(after_family_mutation)
