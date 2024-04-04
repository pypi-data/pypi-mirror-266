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

from pluggy_sdk.models.bills_list200_response import BillsList200Response

class TestBillsList200Response(unittest.TestCase):
    """BillsList200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> BillsList200Response:
        """Test BillsList200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `BillsList200Response`
        """
        model = BillsList200Response()
        if include_optional:
            return BillsList200Response(
                page = 1.337,
                total = 1.337,
                total_pages = 1.337,
                results = [
                    {}
                    ]
            )
        else:
            return BillsList200Response(
        )
        """

    def testBillsList200Response(self):
        """Test BillsList200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
