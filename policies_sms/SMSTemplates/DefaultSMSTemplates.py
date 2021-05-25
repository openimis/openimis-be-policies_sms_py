from django.utils.translation import ugettext as _


class DefaultSMSTemplates:

    def get_all(self):
        output = {}
        for attr in self.__dir__():
            if attr.startswith('__') or type(getattr(self, attr, None)) != str:
                continue
            else:
                output[attr] = getattr(self, attr, None)

        return output

    @property
    def sms_on_activation(self):
        return _("policies_sms.sms_on_activation")

    @property
    def sms_on_effective(self):
        return _("policies_sms.sms_on_effective")

    @property
    def sms_before_expiry(self):
        return _("policies_sms.sms_before_expiry")

    @property
    def sms_on_expiration(self):
        return _("policies_sms.sms_on_expiration")

    @property
    def sms_after_expiry(self):
        return _("policies_sms.sms_after_expiry")

    @property
    def sms_on_renewal(self):
        return _("policies_sms.sms_on_renewal")

    @property
    def sms_control_number_assigned(self):
        return _("policies_sms.sms_control_number_assigned")

    @property
    def sms_control_number_error_bulk_payment(self):
        return _("policies_sms.sms_control_number_error_bulk_payment")

    @property
    def sms_control_number_error_single_payment(self):
        return _("policies_sms.sms_control_number_error_single_payment")

    @property
    def sms_paid_and_activated(self):
        return _("policies_sms.sms_paid_and_activated")

    @property
    def sms_paid_and_not_activated(self):
        return _("policies_sms.sms_paid_and_not_activated")

    @property
    def sms_paid_and_not_matched(self):
        return _("policies_sms.sms_paid_and_not_matched")
