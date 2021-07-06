from django.db.models import Q

from .models import FamilyNotification


class _Modes:
    __modes = FamilyNotification.FamilyComunicationModes
    __phone_exists_query = ~(Q(members__phone__in=[None, '']))
    __approval_exists_query = Q(family_notification__approval_of_notification=True)

    FAMILY_REPORT_MODE_QUERIES = {
        __modes.ALL: Q(),
        __modes.FULL_COMMUNICATION_ENABLED_CODE: __approval_exists_query & __phone_exists_query,
        __modes.APPROVAL_NO_PHONE_NUMBER_CODE: __approval_exists_query & ~__phone_exists_query,
        __modes.NO_APPROVAL_PHONE_NUMBER_CODE: ~__approval_exists_query & __phone_exists_query,
        __modes.NO_APPROVAL_NO_PHONE_NUMBER_CODE: ~__approval_exists_query & ~__phone_exists_query
    }


def communication_approval_filter(family_notification_criterion: FamilyNotification.FamilyComunicationModes) -> Q:
    if family_notification_criterion not in list(map(int, FamilyNotification.FamilyComunicationModes)):
        raise ValueError(f"Given option {family_notification_criterion} for family "
                         f"notification policy is out of scope out of scope.")
    if family_notification_criterion != 0:
        key = FamilyNotification.FamilyComunicationModes(family_notification_criterion)
        mode_filter = _Modes.FAMILY_REPORT_MODE_QUERIES[key]
        return mode_filter
    else:
        return Q()
