from location.models import Location
from policy_notification.models import FamilyNotification
from django.utils.translation import ugettext as _

REPORT_MODE_STRING_REPRESENTATION = {
        FamilyNotification.FamilyComunicationModes.ALL: _('policy_notification.Mode.0'),
        FamilyNotification.FamilyComunicationModes.FULL_COMMUNICATION_ENABLED_CODE: _('policy_notification.Mode.1'),
        FamilyNotification.FamilyComunicationModes.APPROVAL_NO_PHONE_NUMBER_CODE: _('policy_notification.Mode.2'),
        FamilyNotification.FamilyComunicationModes.NO_APPROVAL_PHONE_NUMBER_CODE: _('policy_notification.Mode.3'),
        FamilyNotification.FamilyComunicationModes.NO_APPROVAL_NO_PHONE_NUMBER_CODE: _('policy_notification.Mode.4')
}


class CommunicationByNotificationReportBuilder:

    def build_report_data(self, families, region=None, district=None,
                          enrollment_officer=None, mode=0, other_filters=None):
        mode = FamilyNotification.FamilyComunicationModes(mode)
        return {
            'report_region': self.__location_repr(region) if region else "",
            'report_district': self.__location_repr(district) if district else "",
            'report_mode': REPORT_MODE_STRING_REPRESENTATION[mode],
            'report_officer_code': F"{enrollment_officer.code}" if enrollment_officer else "",
            'report_officer_name':
                F"{enrollment_officer.other_names} {enrollment_officer.last_name}" if enrollment_officer else "",
            'family_sms_list': self.families_to_report_input(families),
            'other_filters': other_filters if other_filters else []
        }

    def families_to_report_input(self, families):
        families_repr = []
        for family in families:
            next_repr = {
                'family_district': self.__location_repr(family.location.parent.parent),
                'family_municipality': self.__location_repr(family.location.parent),
                'family_village': self.__location_repr(family.location),
                'family_head_chf': str(family.head_insuree.chf_id),
                'family_head_given_name': str(family.head_insuree.other_names),
                'family_head_last_name': str(family.head_insuree.last_name),
                'family_notification_approval': str(family.family_notification.approval_of_notification),
                'family_notification_language': str(family.family_notification.language_of_notification),
                'family_head_phone': str(family.head_insuree.phone) if family.head_insuree.phone else '',
                'family_alternative_given_name': '',
                'family_alternative_last_name': '',
                'family_alternative_phone': ''
            }
            if not family.head_insuree.phone or family.head_insuree.phone == '':
                family_member_with_phone = self.__get_family_member_with_phone(family)
                if family_member_with_phone:
                    next_repr.update({
                        'family_alternative_given_name': family_member_with_phone.other_names,
                        'family_alternative_last_name': family_member_with_phone.last_name,
                        'family_alternative_phone': family_member_with_phone.phone
                    })
                else:
                    next_repr.update({
                        'family_alternative_given_name': '-',
                        'family_alternative_last_name': '-',
                        'family_alternative_phone': '-'
                    })
            families_repr.append(next_repr)
        return families_repr

    def __location_repr(self, location: Location) -> str:
        return F"{location.code} {location.name}"

    def __get_family_member_with_phone(self, family):
        query = family.members.filter(phone__isnull=False).exclude(phone='')
        if query.exists():
            return query.first()
        else:
            return None
