from graphene import Context
from core.models import Officer
from django.db.models import Q, QuerySet
from insuree.models import Family
from location.models import Location
from location.apps import LocationConfig
from policy.models import Policy
from policy_notification.filters import communication_approval_filter


class FamilyNotificationReportService(object):

    def __init__(self, request):
        self.user = request.user
        self.context = Context(request=request)
        self.context.user = self.user

    def fetch(self, request):
        mode = int(request.get('mode', 0))
        enrollment_officer_uuid = request.get('officerUuid', None)
        if enrollment_officer_uuid:
            enrollment_officer = Officer.objects.get(uuid=enrollment_officer_uuid)
        else:
            enrollment_officer = None

        if request.get('districtUuid', None):
            district = Location.objects.get(uuid=request.get('districtUuid'))
            region = district.parent
            families = self.fetch_location_families(district=district, mode=mode, enrollment_officer=enrollment_officer)
        elif request.get('regionUuid', None):
            district = None
            region = Location.objects.get(uuid=request.get('regionUuid'))
            families = self.fetch_location_families(region=region, mode=mode, enrollment_officer=enrollment_officer)
        else:
            raise ValueError("Neither regionUuuid nor districtUuid provided")

        return {'families': families,
                'region': region, 'district': district,
                'mode': mode, 'enrollment_officer': enrollment_officer}

    def fetch_location_families(self, region=None, district=None, enrollment_officer=None, mode=0):
        if district:
            families = self.get_filtered_families(district, 2, enrollment_officer, mode)
        elif region:
            families = self.get_filtered_families(region, 1, enrollment_officer, mode)
        else:
            raise ValueError('Either region or district must be specified in order for a report to be generated')

        return families

    def get_filtered_families(self, location: Location, location_level: int,
                              officer: Officer = None, mode: int = 0) -> QuerySet:
        # location level: 1 - region, 2 - district, 3 - municipality, 4 - village

        family_queryset = Family.objects.filter(validity_to__isnull=True)
        family_queryset = self._add_location_filter(family_queryset, location, location_level)

        if officer:
            family_queryset = self._add_officer_filter(family_queryset, officer)

        if mode != 0:
            family_queryset = self._add_mode_filter(family_queryset, mode)

        return family_queryset

    def _add_location_filter(self, family_queryset, location, location_level):
        location_query = "location"
        for i in range(len(LocationConfig.location_types) - location_level):
            location_query = F"{location_query}__parent"
        location_query = Q(**{F"{location_query}__uuid": location.uuid})

        return family_queryset.filter(location_query)

    def _add_officer_filter(self, family_queryset, officer):
        eo_policies_families = Policy.objects \
            .filter(family__id__in=family_queryset.values_list('id', flat=True)) \
            .filter(officer__id=officer.id) \
            .values_list('family', flat=True)

        return family_queryset.filter(id__in=eo_policies_families)

    def _add_mode_filter(self, family_queryset, mode):
        return family_queryset.filter(communication_approval_filter(mode))
