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

from pluggy_sdk.models.connector_credential import ConnectorCredential

class TestConnectorCredential(unittest.TestCase):
    """ConnectorCredential unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ConnectorCredential:
        """Test ConnectorCredential
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ConnectorCredential`
        """
        model = ConnectorCredential()
        if include_optional:
            return ConnectorCredential(
                name = '',
                label = '',
                type = 'text',
                assistive_text = '',
                data = '',
                placeholder = '',
                validation = '',
                validation_message = '',
                mfa = True,
                options = [
                    pluggy_sdk.models.credential_select_option.CredentialSelectOption(
                        value = '', 
                        label = '', )
                    ]
            )
        else:
            return ConnectorCredential(
                name = '',
                label = '',
                type = 'text',
        )
        """

    def testConnectorCredential(self):
        """Test ConnectorCredential"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
