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

from pluggy_sdk.api.webhook_api import WebhookApi


class TestWebhookApi(unittest.TestCase):
    """WebhookApi unit test stubs"""

    def setUp(self) -> None:
        self.api = WebhookApi()

    def tearDown(self) -> None:
        pass

    def test_webhooks_create(self) -> None:
        """Test case for webhooks_create

        Create
        """
        pass

    def test_webhooks_delete(self) -> None:
        """Test case for webhooks_delete

        Delete
        """
        pass

    def test_webhooks_list(self) -> None:
        """Test case for webhooks_list

        List
        """
        pass

    def test_webhooks_retrieve(self) -> None:
        """Test case for webhooks_retrieve

        Retrieve
        """
        pass

    def test_webhooks_update(self) -> None:
        """Test case for webhooks_update

        Update
        """
        pass


if __name__ == '__main__':
    unittest.main()
