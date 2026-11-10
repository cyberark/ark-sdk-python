import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from uuid import uuid4

from pydantic import ValidationError

from ark_sdk_python.common import get_logger
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.sia.workspaces.db import (
    ArkSIADBAddDatabaseTarget,
    ArkSIADBAuthMethodType,
    ArkSIADBDatabaseEngineType,
    ArkSIADBDatabaseFamilyType,
    ArkSIADBDatabaseTargetService,
    ArkSIADBDatabaseTargetsFilter,
    ArkSIADBUpdateDatabaseTarget,
)
from ark_sdk_python.services.sia.workspaces.db.ark_sia_db_workspace_service import ArkSIADBWorkspaceService

NAME_MAX_LENGTH = 256
NORMAL_STR_MAX_LENGTH = 2048
LONG_STR_MAX_LENGTH = 4096
VALID_SECRET_ID = str(uuid4())


def add_target(**overrides) -> ArkSIADBAddDatabaseTarget:
    payload = {
        'name': 'test-db',
        'provider_engine': ArkSIADBDatabaseEngineType.PostgresSHVM,
        'read_write_endpoint': 'db.example.com',
        'configured_auth_method_type': ArkSIADBAuthMethodType.LocalEphemeralUser,
    }
    payload.update(overrides)
    return ArkSIADBAddDatabaseTarget(**payload)


def update_target(**overrides) -> ArkSIADBUpdateDatabaseTarget:
    payload = {'name': 'test-db'}
    payload.update(overrides)
    return ArkSIADBUpdateDatabaseTarget(**payload)


class TestAddDatabaseTargetValidation(unittest.TestCase):
    def test_error_invalid_provider_engine(self):
        """Test that invalid provider engine raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            ArkSIADBAddDatabaseTarget(
                name="test-db",
                provider_engine="invalid_engine",
                read_write_endpoint="db.example.com",
            )

        # Value validation errors use Python field name (snake_case)
        self.assertIn("provider_engine", str(context.exception))

    def test_error_empty_provider_engine(self):
        """Test that empty provider engine raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            ArkSIADBAddDatabaseTarget(
                name="test-db",
                read_write_endpoint="db.example.com",
            )

        # Missing field errors use alias name (camelCase) because of ArkCamelizedModel
        self.assertIn("providerEngine", str(context.exception))

    def test_accepted_payloads(self):
        accepted = {
            'name_at_max_length': {'name': 'n' * NAME_MAX_LENGTH},
            'name_with_inner_whitespace': {'name': 'my test db'},
            'normal_string_at_max_length': {'region': 'r' * NORMAL_STR_MAX_LENGTH},
            'long_string_at_max_length': {'services': ['s' * LONG_STR_MAX_LENGTH]},
            'service_object_item': {'services': [ArkSIADBDatabaseTargetService(service_name='reporting', port=1433)]},
            'port_at_minimum': {'port': 1},
            'port_at_maximum': {'port': 65535},
            'secret_id_as_uuid': {'secret_id': VALID_SECRET_ID},
            'organizational_unit': {'domain_controller_organizational_unit': 'OU=Databases,DC=example,DC=com'},
        }
        for case, overrides in accepted.items():
            with self.subTest(case=case):
                add_target(**overrides)

    def test_rejected_payloads(self):
        rejected = {
            'name_empty': {'name': ''},
            'name_above_max_length': {'name': 'n' * (NAME_MAX_LENGTH + 1)},
            'name_with_leading_whitespace': {'name': ' test-db'},
            'name_with_trailing_whitespace': {'name': 'test-db '},
            'normal_string_above_max_length': {'region': 'r' * (NORMAL_STR_MAX_LENGTH + 1)},
            'normal_string_with_trailing_whitespace': {'region': 'us-east-1 '},
            'organizational_unit_above_max_length': {'domain_controller_organizational_unit': 'o' * (NORMAL_STR_MAX_LENGTH + 1)},
            'organizational_unit_with_trailing_whitespace': {'domain_controller_organizational_unit': 'OU=Databases '},
            'long_string_above_max_length': {'services': ['s' * (LONG_STR_MAX_LENGTH + 1)]},
            'services_item_with_trailing_whitespace': {'services': ['reporting ']},
            'endpoint_empty': {'read_write_endpoint': ''},
            'endpoint_with_inner_whitespace': {'read_write_endpoint': 'db.example .com'},
            'endpoint_with_trailing_whitespace': {'read_write_endpoint': 'db.example.com '},
            'endpoint_above_max_length': {'read_write_endpoint': 'e' * (LONG_STR_MAX_LENGTH + 1)},
            'read_only_endpoint_with_inner_whitespace': {'read_only_endpoint': 'db.example .com'},
            'port_below_range': {'port': 0},
            'port_above_range': {'port': 65536},
            'secret_id_not_a_uuid': {'secret_id': 'not-a-uuid'},
            'platform_atlas': {'platform': ArkWorkspaceType.ATLAS},
            'auth_method_atlas_ephemeral_user': {'configured_auth_method_type': ArkSIADBAuthMethodType.AtlasEphemeralUser},
        }
        for case, overrides in rejected.items():
            with self.subTest(case=case):
                with self.assertRaises(ValidationError):
                    add_target(**overrides)

    def test_organizational_unit_is_sent_to_the_api(self):
        target = add_target(domain_controller_organizational_unit='OU=Databases,DC=example,DC=com')

        payload = target.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(payload['domainControllerOrganizationalUnit'], 'OU=Databases,DC=example,DC=com')


class TestUpdateDatabaseTargetValidation(unittest.TestCase):
    def test_accepted_payloads(self):
        accepted = {
            'new_name_at_max_length': {'new_name': 'n' * NAME_MAX_LENGTH},
            'normal_string_at_max_length': {'region': 'r' * NORMAL_STR_MAX_LENGTH},
            'long_string_at_max_length': {'services': ['s' * LONG_STR_MAX_LENGTH]},
            'service_object_item': {'services': [ArkSIADBDatabaseTargetService(service_name='reporting', port=1433)]},
            'port_at_minimum': {'port': 1},
            'port_at_maximum': {'port': 65535},
            'secret_id_as_uuid': {'secret_id': VALID_SECRET_ID},
            'organizational_unit': {'domain_controller_organizational_unit': 'OU=Databases,DC=example,DC=com'},
        }
        for case, overrides in accepted.items():
            with self.subTest(case=case):
                update_target(**overrides)

    def test_rejected_payloads(self):
        rejected = {
            'name_above_max_length': {'name': 'n' * (NAME_MAX_LENGTH + 1)},
            'name_with_trailing_whitespace': {'name': 'test-db '},
            'new_name_empty': {'new_name': ''},
            'new_name_above_max_length': {'new_name': 'n' * (NAME_MAX_LENGTH + 1)},
            'new_name_with_trailing_whitespace': {'new_name': 'test-db '},
            'normal_string_above_max_length': {'region': 'r' * (NORMAL_STR_MAX_LENGTH + 1)},
            'organizational_unit_with_trailing_whitespace': {'domain_controller_organizational_unit': 'OU=Databases '},
            'long_string_above_max_length': {'services': ['s' * (LONG_STR_MAX_LENGTH + 1)]},
            'services_item_with_trailing_whitespace': {'services': ['reporting ']},
            'endpoint_with_inner_whitespace': {'read_write_endpoint': 'db.example .com'},
            'port_below_range': {'port': 0},
            'port_above_range': {'port': 65536},
            'secret_id_not_a_uuid': {'secret_id': 'not-a-uuid'},
            'platform_atlas': {'platform': ArkWorkspaceType.ATLAS},
            'auth_method_atlas_ephemeral_user': {'configured_auth_method_type': ArkSIADBAuthMethodType.AtlasEphemeralUser},
        }
        for case, overrides in rejected.items():
            with self.subTest(case=case):
                with self.assertRaises(ValidationError):
                    update_target(**overrides)

    def test_organizational_unit_is_sent_to_the_api(self):
        target = update_target(domain_controller_organizational_unit='OU=Databases,DC=example,DC=com')

        payload = target.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(payload['domainControllerOrganizationalUnit'], 'OU=Databases,DC=example,DC=com')


class TestListDatabaseTargets(unittest.TestCase):
    def setUp(self):
        client_patcher = patch('ark_sdk_python.services.sia.workspaces.db.ark_sia_db_workspace_service.ArkISPServiceClient')
        service_init_patcher = patch('ark_sdk_python.services.ark_service.ArkService.__init__', return_value=None)
        mock_client_class = client_patcher.start()
        service_init_patcher.start()
        self.addCleanup(client_patcher.stop)
        self.addCleanup(service_init_patcher.stop)

        self.service = ArkSIADBWorkspaceService(MagicMock())
        self.service._logger = get_logger('TestListDatabaseTargets')  # pylint: disable=protected-access
        self.mock_client = mock_client_class.from_isp_auth.return_value
        self.mock_client.get.return_value = self.__empty_page()

    @staticmethod
    def __empty_page() -> MagicMock:
        response = MagicMock()
        response.status_code = HTTPStatus.OK
        response.json.return_value = {'items': [], 'totalCount': 0, 'nextCursor': None}
        return response

    def test_reported_families_can_be_onboarded(self):
        families = self.service.list_database_target_family_types()

        self.assertTrue(families)
        for family in families:
            self.assertIsInstance(family, ArkSIADBDatabaseFamilyType)
        self.assertNotIn(ArkSIADBDatabaseFamilyType.Unknown, families)

    def test_unsupported_family_is_rejected_without_calling_the_api(self):
        with self.assertRaises(ArkServiceException):
            self.service.list_database_targets_by(ArkSIADBDatabaseTargetsFilter(provider_family=ArkSIADBDatabaseFamilyType.Unknown))
        self.mock_client.get.assert_not_called()

    def test_misspelled_family_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArkSIADBDatabaseTargetsFilter(provider_family='mysql')

    def test_supported_family_is_passed_as_a_query_parameter(self):
        self.service.list_database_targets_by(ArkSIADBDatabaseTargetsFilter(provider_family=ArkSIADBDatabaseFamilyType.Postgres))

        self.assertEqual(self.mock_client.get.call_args.kwargs['params'], {'providerFamily': 'Postgres'})
