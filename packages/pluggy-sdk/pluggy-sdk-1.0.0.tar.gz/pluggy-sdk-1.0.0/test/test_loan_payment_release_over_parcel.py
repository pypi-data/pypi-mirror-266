# coding: utf-8

"""
    Pluggy API

    Pluggy's main API to review data and execute connectors

    The version of the OpenAPI document: 1.0.0
    Contact: hello@pluggy.ai
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from pluggy_sdk.models.loan_payment_release_over_parcel import LoanPaymentReleaseOverParcel

class TestLoanPaymentReleaseOverParcel(unittest.TestCase):
    """LoanPaymentReleaseOverParcel unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> LoanPaymentReleaseOverParcel:
        """Test LoanPaymentReleaseOverParcel
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `LoanPaymentReleaseOverParcel`
        """
        model = LoanPaymentReleaseOverParcel()
        if include_optional:
            return LoanPaymentReleaseOverParcel(
                fees = [
                    pluggy_sdk.models.loan_payment_release_over_parcel_fee.LoanPaymentReleaseOverParcelFee(
                        name = '', 
                        code = '', 
                        amount = 1.337, )
                    ],
                charges = [
                    pluggy_sdk.models.loan_payment_release_over_parcel_charge.LoanPaymentReleaseOverParcelCharge(
                        type = '', 
                        additional_info = '', 
                        amount = 1.337, )
                    ]
            )
        else:
            return LoanPaymentReleaseOverParcel(
        )
        """

    def testLoanPaymentReleaseOverParcel(self):
        """Test LoanPaymentReleaseOverParcel"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
