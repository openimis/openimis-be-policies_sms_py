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
        return _(
            "The policy for the family/group "
            "%(InsuranceID)s - %(Name)s with the insurance product "
            "%(ProductCode)s -   %(ProductName)s  has been activated from the date "
            "%(EffectiveDate)s until the expiry date  %(ExpiryDate)s. "
        )

    @property
    def sms_on_effective(self):
        return _(
            "The policy for the family/group %(InsuranceID)s - "
            "%(Name)s with the insurance product %(ProductCode)s -   "
            "%(ProductName)s  starts insurance coverage today and expires on  "
            "%(ExpiryDate)s.    "
        )

    @property
    def sms_before_expiry(self):
        return _(
            "The policy for the family/group %(InsuranceID)s - "
            "%(Name)s with the insurance product %(ProductCode)s -   "
            "%(ProductName)s  will expire on  %(ExpiryDate)s.  "
            "Its renewal is recommended. "
        )

    @property
    def sms_on_expiration(self):
        return _(
            "The policy for the family/group %(InsuranceID)s - %(Name)s "
            "with the insurance product %(ProductCode)s -   %(ProductName)s "
            " expires today and it has not been renewed yet.   "
        )

    @property
    def sms_after_expiry(self):
        return _(
            "The policy for the family/group %(InsuranceID)s - "
            "%(Name)s with the insurance product %(ProductCode)s -   %(ProductName)s  "
            "expired on  %(ExpiryDate)s  and it hasn’t been renewed yet.  "
            "Its renewal is recommended. "
        )

    @property
    def sms_on_renewal(self):
        return _(
            "The policy for the family/group %(InsuranceID)s - "
            "%(Name)s with the insurance product %(ProductCode)s -   "
            "%(ProductName)s  has been renewed from the date "
            "%(EffectiveDate)s until the expiry date  %(ExpiryDate)s. "
        )

    @property
    def sms_control_number_assigned(self):
        return _(
            "The control number %(ControlNumber)s was assigned for "
            "the request issued on %(DateRequest)s at  %(TimeRequest)s "
            "for payment of the set of policies containing the family/group "
            "%(InsuranceID)s - %(Name)s  with the insurance product %(ProductCode)s  -  "
            "%(ProductCode)s  and alltogether %(NumberPolicies)s policies.   "
            "The amount of payment associated with the request is %(AmountToBePaid)s.  "
        )

    @property
    def sms_control_number_error_bulk_payment(self):
        return _(
            "The control number %(ControlNumber)s cannot be assigned for "
            "the request issued on %(DateRequest)s at  %(TimeRequest)s for "
            "payment of the set of policies containing the family/group "
            "%(InsuranceID)s - %(Name)s  with the insurance product %(ProductCode)s  "
            "-  %(ProductCode)s  and alltogether %(NumberPolicies)s policies.  "
            "The reason is %(ErrorMessage)s. "
        )

    @property
    def sms_control_number_error_single_payment(self):
        return _(
            "The control number %(ControlNumber)s cannot be assigned for the request issued on "
            "%(DateRequest)s at  %(TimeRequest)s for payment of the policy for the family/group %(InsuranceID)s  "
            "with the insurance product %(ProductCode)s .   The reason is %(ErrorMessage)s"
        )

    @property
    def sms_paid_and_activated(self):
        return _(
            "The payment %(Payment)s performed on %(DatePayment)s for the "
            "control number %(ControlNumber)s received  and the "
            "policy for the family/group %(InsuranceID)s - %(Name)s "
            "with the insurance product %(ProductCode)s -   %(ProductName)s  "
            "activated from the date %(EffectiveDate)s until the expiry date  %(ExpiryDate)s.    "
            "The allocated payment for the policy is  %(Payment)s."
        )

    @property
    def sms_paid_and_not_activated(self):
        return _(
            "The payment %(Payment)s performed on %(DatePayment)s for the control number "
            "%(ControlNumber)s received  but the policy for the family/group "
            "%(InsuranceID)s - %(Name)s with the insurance product %(ProductCode)s "
            "-   %(ProductName)s  has not been activated.    "
            "The allocated payment for the policy is  %(Payment)s  "
            "but still %(PaymentLeft)s  should be paid for activation of the policy."
        )

    @property
    def sms_paid_and_not_matched(self):
        return _(
            "The payment %(Payment)s performed on %(DatePayment)s for the control number %(ControlNumber)s received "
            "but the policies in the set containing  the family/group %(InsuranceID)s - %(Name)s with the insurance "
            "product %(ProductCode)s -   %(ProductName)s  cannot be matched for time being"
        )
