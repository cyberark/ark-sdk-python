import argparse
import unittest

from pydantic import ValidationError

from ark_sdk_python.args import ArkPydanticArgparse
from ark_sdk_python.models.actions.services.ark_ars_exec_action_consts import ARS_REQUESTS_ACTIONS
from ark_sdk_python.models.services.ars.requests import ArkARSSubmitAccessRequest
from ark_sdk_python.services.ars.requests import ArkARSRequestsService


class TestArkARSRequestsActions(unittest.TestCase):
    def test_every_action_maps_to_a_service_method(self):
        for action in ARS_REQUESTS_ACTIONS.schemas:
            self.assertTrue(hasattr(ArkARSRequestsService, action.replace('-', '_')), f'missing service method for [{action}]')

    def test_submit_is_an_async_action(self):
        self.assertIs(ARS_REQUESTS_ACTIONS.schemas['submit-access-request'], ArkARSSubmitAccessRequest)
        self.assertIn('submit-access-request', ARS_REQUESTS_ACTIONS.async_actions)

    def test_submit_cli_args_parse_request_details(self):
        schema = ArkARSSubmitAccessRequest.model_json_schema()
        parser = argparse.ArgumentParser()
        ArkPydanticArgparse.schema_to_argparse(schema, parser)
        args = parser.parse_args(
            [
                '--target-category',
                'VM',
                '--request-type',
                'DUAL_CONTROL',
                '--request-details',
                'target_type=Linux',
                'target_address=vm.local.com',
                '--wait-until-finished',
            ]
        )
        request = ArkARSSubmitAccessRequest.model_validate(ArkPydanticArgparse.argparse_to_schema(schema, args))
        self.assertEqual(request.request_type, 'DUAL_CONTROL')
        self.assertEqual(request.request_details, {'target_type': 'Linux', 'target_address': 'vm.local.com'})
        self.assertTrue(request.wait_until_finished)

    def test_submit_requires_request_details(self):
        schema = ArkARSSubmitAccessRequest.model_json_schema()
        self.assertIn('requestDetails', schema['required'])
        with self.assertRaises(ValidationError):
            ArkARSSubmitAccessRequest(target_category='VM')


if __name__ == '__main__':
    unittest.main()
