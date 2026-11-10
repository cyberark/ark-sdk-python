import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services.ars.requests import ArkARSAccessRequestForms, ArkARSListAccessRequestForms
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request_form import ArkARSConditionalField, ArkARSQueryValueType
from ark_sdk_python.models.services.ars.requests.ark_ars_request_type import ArkARSRequestType
from ark_sdk_python.services.ars.requests.ark_ars_requests_service import REQUEST_FORMS_ROUTE, ArkARSRequestsService

REQUEST_FORMS_RESPONSE = {
    'requestForms': [
        {
            'targetCategory': 'CLOUD_CONSOLE',
            'requestType': 'ON_DEMAND',
            'requestForm': {
                'questions': [
                    {
                        'key': 'location_type',
                        'required': True,
                        'title': 'Location Type',
                        'description': 'Location type',
                        'valueType': 'CHOICE',
                        'valueChoices': ['AWS', 'GCP', 'Azure'],
                    },
                    {
                        'key': 'org_id',
                        'required': {
                            'operator': 'OR',
                            'conditions': [
                                {'name': 'regex_condition', 'key': 'location_type', 'condition': '^(GCP|Azure)$'},
                                {'name': 'regex_condition', 'key': 'role_id', 'condition': '^arn:aws:sso'},
                            ],
                        },
                        'title': 'ORG ID',
                        'valueType': 'STRING',
                        'validators': [{'name': 'type_checker_validator'}],
                    },
                    {
                        'key': 'priority',
                        'required': True,
                        'default': 'Medium',
                        'valueType': 'CHOICE',
                        'valueChoices': ['High', 'Medium', 'Low'],
                    },
                ]
            },
        }
    ]
}


class TestArkARSRequestsServiceRequestForms(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.patches = [
            patch(
                'ark_sdk_python.services.ars.requests.ark_ars_requests_service.ArkISPServiceClient.from_isp_auth',
                return_value=self.mock_client,
            ),
            patch('ark_sdk_python.services.ars.requests.ark_ars_requests_service.os.getenv', return_value='prod'),
            patch('ark_sdk_python.services.ars.requests.ark_ars_requests_service.ArkService.__init__', return_value=None),
        ]
        for patcher in self.patches:
            patcher.start()
        self.service = ArkARSRequestsService(MagicMock())
        self.service._logger = MagicMock()  # pylint: disable=protected-access

    def tearDown(self):
        for patcher in self.patches:
            patcher.stop()

    def _mock_response(self, status_code: int, json_body=None, text: str = '') -> MagicMock:
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        response.json.return_value = json_body
        self.mock_client.get.return_value = response
        return response

    def test_list_access_request_forms_sends_filters_as_query_params(self):
        self._mock_response(HTTPStatus.OK, REQUEST_FORMS_RESPONSE)
        self.service.list_access_request_forms(
            ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE', request_type=ArkARSRequestType.DUAL_CONTROL)
        )
        self.mock_client.get.assert_called_once_with(
            REQUEST_FORMS_ROUTE, params={'targetCategory': 'CLOUD_CONSOLE', 'requestType': 'DUAL_CONTROL'}
        )

    def test_list_access_request_forms_defaults_to_on_demand(self):
        self._mock_response(HTTPStatus.OK, REQUEST_FORMS_RESPONSE)
        self.service.list_access_request_forms(ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE'))
        _, kwargs = self.mock_client.get.call_args
        self.assertEqual(kwargs['params']['requestType'], 'ON_DEMAND')

    def test_list_access_request_forms_parses_response(self):
        self._mock_response(HTTPStatus.OK, REQUEST_FORMS_RESPONSE)
        result = self.service.list_access_request_forms(ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE'))
        self.assertIsInstance(result, ArkARSAccessRequestForms)
        self.assertEqual(len(result.request_forms), 1)
        form = result.request_forms[0]
        self.assertEqual(form.target_category, ArkCategoryType.CLOUD_CONSOLE)
        self.assertEqual(form.request_type, ArkARSRequestType.ON_DEMAND)
        questions = {question.key: question for question in form.request_form.questions}
        self.assertEqual(list(questions), ['location_type', 'org_id', 'priority'])
        self.assertIs(questions['location_type'].required, True)
        self.assertEqual(questions['location_type'].value_type, ArkARSQueryValueType.choice)
        self.assertEqual(questions['location_type'].value_choices, ['AWS', 'GCP', 'Azure'])
        self.assertIsInstance(questions['org_id'].required, ArkARSConditionalField)
        self.assertEqual([c.key for c in questions['org_id'].required.conditions], ['location_type', 'role_id'])
        self.assertEqual(questions['org_id'].validators[0].name, 'type_checker_validator')
        self.assertEqual(questions['priority'].default, 'Medium')

    def test_list_access_request_forms_empty_response(self):
        self._mock_response(HTTPStatus.OK, {'requestForms': []})
        result = self.service.list_access_request_forms(ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE'))
        self.assertEqual(result.request_forms, [])

    def test_list_access_request_forms_raises_on_error_status(self):
        self._mock_response(HTTPStatus.UNPROCESSABLE_ENTITY, text='The specified category type input is invalid')
        with self.assertRaises(ArkServiceException) as ctx:
            self.service.list_access_request_forms(ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE'))
        self.assertIn('Failed to list access request forms', str(ctx.exception))

    def test_list_access_request_forms_raises_on_invalid_payload(self):
        self._mock_response(HTTPStatus.OK, {'requestForms': [{'targetCategory': 'CLOUD_CONSOLE'}]})
        with self.assertRaises(ArkServiceException) as ctx:
            self.service.list_access_request_forms(ArkARSListAccessRequestForms(target_category='CLOUD_CONSOLE'))
        self.assertIn('Failed to parse access request forms response', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
