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

from pluggy_sdk.models.investment_expenses import InvestmentExpenses

class TestInvestmentExpenses(unittest.TestCase):
    """InvestmentExpenses unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> InvestmentExpenses:
        """Test InvestmentExpenses
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `InvestmentExpenses`
        """
        model = InvestmentExpenses()
        if include_optional:
            return InvestmentExpenses(
                service_tax = 1.337,
                brokerage_fee = 1.337,
                income_tax = 1.337,
                trading_assets_notice_fee = 1.337,
                maintenance_fee = 1.337,
                settlement_fee = 1.337,
                clearing_fee = 1.337,
                stock_exchange_fee = 1.337,
                custody_fee = 1.337,
                operating_fee = 1.337,
                other = 1.337
            )
        else:
            return InvestmentExpenses(
        )
        """

    def testInvestmentExpenses(self):
        """Test InvestmentExpenses"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
