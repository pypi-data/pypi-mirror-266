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

from pluggy_sdk.models.payment_recipients_institution_list200_response import PaymentRecipientsInstitutionList200Response

class TestPaymentRecipientsInstitutionList200Response(unittest.TestCase):
    """PaymentRecipientsInstitutionList200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PaymentRecipientsInstitutionList200Response:
        """Test PaymentRecipientsInstitutionList200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PaymentRecipientsInstitutionList200Response`
        """
        model = PaymentRecipientsInstitutionList200Response()
        if include_optional:
            return PaymentRecipientsInstitutionList200Response(
                page = 1.337,
                total = 1.337,
                total_pages = 1.337,
                results = [
                    {"id":"5e9f8f8f-f8f8-4f8f-8f8f-8f8f8f8f8f8f","name":"Banco J. Safra S.A.","ispb":"03017677","tradeName":"Banco Safra","compe":"074","createdAt":"2020-04-21T15:00:00.000Z","updatedAt":"2020-04-21T15:00:00.000Z"}
                    ]
            )
        else:
            return PaymentRecipientsInstitutionList200Response(
        )
        """

    def testPaymentRecipientsInstitutionList200Response(self):
        """Test PaymentRecipientsInstitutionList200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
