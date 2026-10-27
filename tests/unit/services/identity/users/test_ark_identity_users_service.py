import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.common import get_logger
from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services.identity.users import ArkIdentityGetUserState, ArkIdentityListUserRoles
from ark_sdk_python.services.identity.users.ark_identity_users_service import ArkIdentityUsersService


class UsersServiceTestCase(unittest.TestCase):
    def setUp(self):
        service_init_patcher = patch('ark_sdk_python.services.ark_service.ArkService.__init__', return_value=None)
        service_init_patcher.start()
        self.addCleanup(service_init_patcher.stop)

        self.service = ArkIdentityUsersService.__new__(ArkIdentityUsersService)
        self.service._logger = get_logger('TestIdentityUsers')  # pylint: disable=protected-access
        self.service._url_prefix = 'api/idadmin/'  # pylint: disable=protected-access
        self.mock_client = MagicMock()
        self.service._client = self.mock_client  # pylint: disable=protected-access

    def _respond(self, status_code=HTTPStatus.OK, body=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = str(body)
        response.json.return_value = body
        self.mock_client.post.return_value = response


class TestListUserRoles(UsersServiceTestCase):
    def test_lists_the_roles_of_the_user(self):
        self._respond(
            body={
                'success': True,
                'Result': {'Results': [{'Row': {'ID': 'r1', 'Name': 'n1', 'RoleName': 'Role One', 'DistinguishedName': 'dn'}}]},
            }
        )
        roles = self.service.list_user_roles(ArkIdentityListUserRoles(user_id='u1'))
        self.mock_client.post.assert_called_once_with('api/idadmin/UserMgmt/GetUsersRolesAndAdministrativeRights', json={'id': 'u1'})
        self.assertEqual([(r.role_id, r.name, r.role_name, r.distinguished_name) for r in roles], [('r1', 'n1', 'Role One', 'dn')])

    def test_user_without_roles_returns_empty(self):
        self._respond(body={'success': True, 'Result': {'Results': []}})
        self.assertEqual(self.service.list_user_roles(ArkIdentityListUserRoles(user_id='u1')), [])

    def test_failure_raises(self):
        self._respond(body={'success': False})
        with self.assertRaises(ArkServiceException):
            self.service.list_user_roles(ArkIdentityListUserRoles(user_id='u1'))

    def test_http_error_raises(self):
        self._respond(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, body={})
        with self.assertRaises(ArkServiceException):
            self.service.list_user_roles(ArkIdentityListUserRoles(user_id='u1'))

    def test_username_is_resolved_to_id(self):
        self.service.user_id_by_name = MagicMock(return_value='u9')
        self._respond(body={'success': True, 'Result': {'Results': []}})
        self.service.list_user_roles(ArkIdentityListUserRoles(username='a@t'))
        self.assertEqual(self.mock_client.post.call_args.kwargs['json'], {'id': 'u9'})

    def test_user_is_required(self):
        with self.assertRaises(ValueError):
            ArkIdentityListUserRoles()


class TestUserState(UsersServiceTestCase):
    def test_active_user(self):
        self._respond(body={'success': True, 'Result': {'State': 'None'}})
        state = self.service.user_state(ArkIdentityGetUserState(user_id='u1', directory_service_uuid='d1'))
        self.mock_client.post.assert_called_once_with(
            'api/idadmin/UserMgmt/GetUserAttributes', json={'ID': 'u1', 'DirectoryServiceUuid': 'd1'}
        )
        self.assertTrue(state.is_active)

    def test_restricted_states_are_inactive(self):
        for restricted in ('Locked', 'Disabled', 'Expired'):
            self._respond(body={'success': True, 'Result': {'State': restricted}})
            state = self.service.user_state(ArkIdentityGetUserState(user_id='u1'))
            self.assertEqual(state.state, restricted)
            self.assertFalse(state.is_active)

    def test_failure_raises(self):
        self._respond(body={'success': False})
        with self.assertRaises(ArkServiceException):
            self.service.user_state(ArkIdentityGetUserState(user_id='u1'))
