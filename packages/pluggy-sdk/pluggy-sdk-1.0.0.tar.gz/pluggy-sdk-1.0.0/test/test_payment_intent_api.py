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

from pluggy_sdk.api.payment_intent_api import PaymentIntentApi


class TestPaymentIntentApi(unittest.TestCase):
    """PaymentIntentApi unit test stubs"""

    def setUp(self) -> None:
        self.api = PaymentIntentApi()

    def tearDown(self) -> None:
        pass

    def test_payment_intent_create(self) -> None:
        """Test case for payment_intent_create

        Create
        """
        pass

    def test_payment_intent_retrieve(self) -> None:
        """Test case for payment_intent_retrieve

        Retrieve
        """
        pass

    def test_payment_intents_list(self) -> None:
        """Test case for payment_intents_list

        List
        """
        pass


if __name__ == '__main__':
    unittest.main()
