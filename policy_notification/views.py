from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from report.services import ReportService
from django.utils.translation import ugettext as _
from policy_notification.apps import PolicyNotificationConfig
from policy_notification.reports import COMMUNICATION_BY_NOTIFICATION_REPORT_TEMPLATE, \
    FamilyNotificationReportServiceGQL
from policy_notification.reports.communication_by_notification.report_builder import \
    CommunicationByNotificationReportBuilder
from policy_notification.reports.communication_by_notification.report_service import FamilyNotificationReportService


@csrf_exempt
def family_policy_notification_report(request):
    if not request.user.has_perms(PolicyNotificationConfig.family_policy_notification_report_perms):
        raise PermissionDenied(_("unauthorized"))

    template = COMMUNICATION_BY_NOTIFICATION_REPORT_TEMPLATE
    report_service = ReportService(request.user)

    qgl_filter = request.GET.get('familyFilterJson', None)
    report_data_service = FamilyNotificationReportService(request) \
        if not qgl_filter else FamilyNotificationReportServiceGQL(request)
    data = report_data_service.fetch(request.GET)

    report_builder = CommunicationByNotificationReportBuilder()

    return report_service.process(
        'family_policy_notification_report',
        report_builder.build_report_data(**data),
        template
    )
