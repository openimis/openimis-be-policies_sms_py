from collections import defaultdict
from functools import lru_cache

import re
import json
from graphene import Context, Schema
from insuree.models import Family
from location.models import Location
from insuree.schema import Query as FamilyGQLQuery
from core.models import Officer


class FamilyNotificationReportServiceGQL(object):
    LOCATION_FILTER_PATTERN = "^parentLocation:\ \"(.*)\"\, parentLocationLevel:\ (.*)$"
    OFFICER_PATTERN = "^officer:\ \"(.*)\"$"
    ADDITIONAL_FILTER_PATTERN = "^additionalFilter:\ \"(.*)\"$"

    def __init__(self, request):
        self.user = request.user
        self.context = Context(request=request)
        self.context.user = self.user

    def fetch(self, request):
        filters = request.get('familyFilterJson', None)
        if not filters:
            raise ValueError("request.GET has to contain familyFilterJson with graphql filters inside.")

        filters = json.loads(filters)
        family_uuids = self._run_families_uuid_gql_query(filters)
        families_location = self._get_location_from_filters(filters)
        mode = self._get_mode_from_filters(filters)
        officer = self._get_eo_from_filters(filters)
        families = Family.objects.filter(uuid__in=family_uuids)
        other_filters = self._get_additional_filters(filters)
        return {'families': families, 'mode': mode, 'enrollment_officer': officer,
                'other_filters': other_filters, **families_location}

    def __filters_to_gql(self, filters):
        query_string = ", ".join(F"{b}" for _, b in filters.items())
        query_string = F"({query_string})" if query_string else ""
        body = """
        edges {
            node {
                uuid
            }
        }"""
        gql_query = F" query {{ " \
                    F"     families{query_string} {{ {body} }}" \
                    F"}}"
        return gql_query

    def _get_location_from_filters(self, filters):
        found = {}
        for loc_filter in [f for f in filters.values() if 'Location' in f]:
            location_pattern = re.search(self.LOCATION_FILTER_PATTERN, loc_filter)
            if location_pattern:
                found[int(location_pattern.group(2))] = location_pattern.group(1)

        # get lowest location level
        if not found:
            raise ValueError("At least region filter is required")

        lowest_location_level = max(found.keys())
        location = Location.objects.get(uuid=found[lowest_location_level])

        # get parent locations as long as it's not at least district
        while lowest_location_level >= 2:
            location = location.parent
            lowest_location_level -= 1

        if lowest_location_level == 1:
            return {'district': location, 'region': location.parent}
        elif lowest_location_level == 0:
            return {'region': location}
        else:
            raise ValueError(f"Invalid location level {lowest_location_level}, expected 0 - region or 1 - district")

    def _run_families_uuid_gql_query(self, filters):
        schema = self.__get_schema()
        query = self.__filters_to_gql(filters)
        families = schema.execute(query, context=self.context).data
        return [x['node']['uuid'] for x in families['families']['edges']]

    def _get_mode_from_filters(self, filters):
        mode = 0
        for add_filter in [f for f in filters.values() if 'additionalFilter' in f]:
            filter = re.search(self.ADDITIONAL_FILTER_PATTERN, add_filter)
            json_str = filter.group(1).replace("\\", "")
            repr = json.loads(json_str)
            mode = repr.get('policyNotification', {}).get('mode', {}).get('value', 0)
        return mode

    def _get_eo_from_filters(self, filters):
        # TODO: Add EO filter to family first
        for officer_filter in [f for f in filters.values() if 'officer' in f]:
            officer = re.search(self.OFFICER_PATTERN, officer_filter)
            officer_uuid = officer.group(1)
            return Officer.objects.get(uuid=officer_uuid)
        return None

    def _get_additional_filters(self, filters):
        """
        Create representation for additionally used filters. Regex patterns from __additional_filters_representation()
        keys are used for determine representation. If filter matches patterns from
        __patterns_for_filters_omitted_in_additional() it's omitted. If the pattern does not match the previous
        conditions the filter is included without any additional changes.
        :param filters: dict with family gql filters, { '1': 'filtered_field: filtered_value', '2': ... }
        :return: list of additional filters representations
        """
        additional_filters = []
        for index, filter_str in filters.items():
            if any(True for x in self.__patterns_for_filters_omitted_in_additional() if re.search(x, filter_str)):
                continue
            filter_report_repr = self.__filter_representation(filter_str)
            if filter_report_repr is not None:
                additional_filters.append(filter_report_repr)
        return additional_filters

    def __filter_representation(self, filter):
        for pattern, action in self.__additional_filters_representation().items():
            matching_pattern = re.search(pattern, filter)
            if matching_pattern:
                return action(matching_pattern.groups())
        return filter

    @lru_cache(maxsize=1)
    def __patterns_for_filters_omitted_in_additional(self):
        return [
            "^parentLocation:\ \"(.*)\"\, parentLocationLevel:\ 0$",
            "^parentLocation:\ \"(.*)\"\, parentLocationLevel:\ 1$",
            self.OFFICER_PATTERN,
            "(.*)policyNotification(.*)mode(.*)"
        ]

    @lru_cache(maxsize=1)
    def __additional_filters_representation(self):
        __MEMBER_REPR = {
            'headInsuree': 'Head',
            'members': 'Member'
        }

        __LOCATION_LEVEL_REPR = {
            '2': 'Municipality',
            '3': 'Village',
            '1': 'District',
            '0': 'Region',
        }

        return {
            # regex_pattern: value_repr_function(regex_groups)
            "(.*)_ChfId_Istartswith: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} CHF starts with: {x[1]}',
            "(.*)_LastName_Icontains: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Last Name contains: {x[1]}',
            "(.*)_OtherNames_Icontains: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Other Names contains: {x[1]}',
            "(.*)_Gender_Code: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Gender code: {x[1]}',
            "(.*)_Dob_Gte: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Birth after: {x[1]}',
            "(.*)_Dob_Lte: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Birth before: {x[1]}',
            "(.*)_Phone_Icontains: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Phone contains: {x[1]}',
            "(.*)_Email_Icontains: \"(.*)\"":
                lambda x: F'{__MEMBER_REPR.get(x[0], x[0])} Email contains: {x[1]}',
            "nullAsFalsePoverty: (.*)": lambda x: F"Poverty Status: {x[0]}",
            self.LOCATION_FILTER_PATTERN:
                lambda x: F'{__LOCATION_LEVEL_REPR.get(x[1], x[1])}: {Location.objects.get(uuid=x[0])}'
        }

    @classmethod
    @lru_cache(maxsize=1)
    def __get_schema(cls):
        from openIMIS.schema import schema
        return schema





