from core.models import User, TechnicalUser, InteractiveUser
from core.test_helpers import create_test_officer
from location.models import Location
from django.test import TestCase, RequestFactory

from insuree.test_helpers import create_test_insuree
from product.test_helpers import create_test_product
from policy.test_helpers import create_test_policy
from policy_notification.reports import FamilyNotificationReportService, FamilyNotificationReportServiceGQL
from policy_notification.reports.communication_by_notification.report_builder import \
    CommunicationByNotificationReportBuilder
from policy_notification.services import *
from django.utils.translation import gettext as _


class TestFamilyNotificationReportServices(TestCase):
    TEST_MODE = 1
    TEST_MODE_REPR = _('policy_notification.Mode.1')

    def setUp(self):
        super(TestFamilyNotificationReportServices, self).setUp()
        self.factory = RequestFactory()
        self.test_user = User(
            username='always_valid',
            t_user=TechnicalUser(username='always_valid'),
            i_user=InteractiveUser.objects.first())
        self.test_officer = create_test_officer()

        self.create_family()
        self.create_location()
        self.create_policy()

    def test_fetch_report_data_region(self):
        get_req_params = {
            'regionUuid': self.test_region.uuid,
            'officerUuid': self.test_officer.uuid,
            'mode': self.TEST_MODE  # Phone number available and approval given
        }
        uri = F'policy_notification/communication_by_notification_report/'
        request = self.factory.get(uri, get_req_params)
        request.user = self.test_user
        service = FamilyNotificationReportService(request)
        report_data = service.fetch(request.GET)
        self.assertEqual(report_data['district'], None)
        self.assertEqual(self.test_region, report_data['region'])
        self.assertEqual(self.test_officer, report_data['enrollment_officer'])
        self.assertEqual(report_data['mode'], self.TEST_MODE)
        self.assertTrue(self.test_family in report_data['families'])

    def test_fetch_report_data_district(self):
        get_req_params = {
            'districtUuid': self.test_district.uuid,
            'regionUuid': self.test_region.uuid,
            'officerUuid': self.test_officer.uuid,
            'mode': self.TEST_MODE  # Phone number available and approval given
        }
        uri = F'policy_notification/communication_by_notification_report/'
        request = self.factory.get(uri, get_req_params)
        request.user = self.test_user
        service = FamilyNotificationReportService(request)
        report_data = service.fetch(request.GET)
        self.assertEqual(report_data['district'], self.test_district)
        self.assertEqual(self.test_region, report_data['region'])
        self.assertEqual(self.test_officer, report_data['enrollment_officer'])
        self.assertEqual(report_data['mode'], self.TEST_MODE)
        self.assertTrue(self.test_family in report_data['families'])

    def test_fetch_report_graphql(self):
        get_req_params = {
            'familyFilterJson': rf'{{"0":"parentLocation: \"{self.test_district.uuid}\", '
                                rf'parentLocationLevel: 1","1":"officer: \"{self.test_officer.uuid}\"",'
                                r'"2":"nullAsFalsePoverty: false",'
                                rf'"3":"additionalFilter: \"{{\\\"policyNotification\\\":{{\\\"mode\\\":{{\\\"id\\\":\\\"mode\\\",\\\"value\\\":{self.TEST_MODE}}}}}}}\""}}',
        }
        uri = F'policy_notification/communication_by_notification_report/'
        request = self.factory.get(uri, get_req_params)
        request.user = self.test_user
        service = FamilyNotificationReportServiceGQL(request)
        report_data = service.fetch(request.GET)
        self.assertEqual(report_data['district'], self.test_district)
        self.assertEqual(self.test_region, report_data['region'])
        self.assertEqual(self.test_officer, report_data['enrollment_officer'])
        self.assertEqual(report_data['mode'], self.TEST_MODE)
        self.assertTrue(self.test_family in report_data['families'])

    def test_report_builder(self):
        get_req_params = {
            'districtUuid': self.test_district.uuid,
            'regionUuid': self.test_region.uuid,
            'officerUuid': self.test_officer.uuid,
            'mode': self.TEST_MODE  # Phone number available and approval given
        }
        uri = F'policy_notification/communication_by_notification_report/'
        request = self.factory.get(uri, get_req_params)
        request.user = self.test_user
        service = FamilyNotificationReportService(request)
        report_data = service.fetch(request.GET)
        builder = CommunicationByNotificationReportBuilder()
        report_data = builder.build_report_data(**report_data)

        self.assertTrue(self.test_region.code in report_data['report_region'])
        self.assertTrue(self.test_district.code in report_data['report_district'])
        self.assertTrue(self.test_officer.last_name in report_data['report_officer_name'])
        self.assertEqual(report_data['report_mode'], self.TEST_MODE_REPR)
        self.assertEqual(report_data['report_officer_code'], self.test_officer.code)
        self.assertEqual(report_data['other_filters'], [])

        family_list = report_data['family_sms_list']
        self.assertTrue(len(family_list) == 1)

        family_list = family_list[0]
        self.assertTrue(self.test_district.code in family_list['family_district'])
        self.assertTrue(self.test_family.location.parent.code in family_list['family_municipality'])
        self.assertTrue(self.test_family.location.code in family_list['family_village'])
        self.assertEqual(family_list['family_head_chf'], self.test_family.head_insuree.chf_id)
        self.assertEqual(family_list['family_head_given_name'], self.test_family.head_insuree.other_names)
        self.assertEqual(family_list['family_head_last_name'], self.test_family.head_insuree.last_name)
        self.assertEqual(bool(family_list['family_notification_approval']),
                         self.test_family.family_notification.approval_of_notification)
        self.assertEqual(family_list['family_notification_language'],
                         self.test_family.family_notification.language_of_notification)
        self.assertEqual(family_list['family_head_phone'], self.test_family.head_insuree.phone)
        self.assertEqual(family_list['family_alternative_given_name'], '')
        self.assertEqual(family_list['family_alternative_last_name'], '')
        self.assertEqual(family_list['family_alternative_phone'], '')

    def create_policy(self):
        self.test_product = create_test_product("PROD1111", custom_props={
            "max_members": 5,
            "administration_period": 0,
            "lump_sum": 0,
            "premium_adult": 300,
            "premium_child": 200,
            "registration_lump_sum": 250,
            "general_assembly_lump_sum": 130,
            "insurance_period": 12,
        })

        self.policy = create_test_policy(product=self.test_product, insuree=self.test_insuree, custom_props={
            "status": 2,
            "validity_from": datetime(2021, 6, 1, 10),
            "officer": self.test_officer
        })

    def create_family(self):
        self.test_insuree = create_test_insuree(with_family=True, custom_props={'phone': '123755'})
        self.test_family = self.test_insuree.family
        self.test_family.location = Location.objects.filter(type='V').first()
        self.test_family.save()

        self.family_notification_policy = \
            create_family_notification_policy(
                self.test_family.uuid,
                {'approvalOfNotification': True, 'languageOfNotification': 'en'}
            )

    def create_location(self):
        self.test_district = self.test_family.location.parent.parent
        self.test_region = self.test_district.parent
