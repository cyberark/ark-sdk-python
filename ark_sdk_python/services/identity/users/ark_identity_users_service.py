from datetime import datetime, timezone
from http import HTTPStatus
from typing import Final

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.roles import ArkIdentityAddUserToRole
from ark_sdk_python.models.services.identity.users import (
    ArkIdentityCreateUser,
    ArkIdentityDeleteUser,
    ArkIdentityResetUserPassword,
    ArkIdentityUpdateUser,
    ArkIdentityUser,
    ArkIdentityUserByName,
    ArkIdentityUserIdByName,
    ArkIdentityUserInfo,
)
from ark_sdk_python.services.identity.common import ArkIdentityBaseService
from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService
from ark_sdk_python.services.identity.roles import ArkIdentityRolesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-users', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

TENANT_SUFFIX_URL: Final[str] = 'Core/GetCdsAliasesForTenant'
CREATE_USER_URL: Final[str] = 'CDirectoryService/CreateUser'
UPDATE_USER_URL: Final[str] = 'CDirectoryService/ChangeUser'
DELETE_USER_URL: Final[str] = 'UserMgmt/RemoveUsers'
RESET_USER_PASSWORD_URL: Final[str] = 'UserMgmt/ResetUserPassword'
REDROCK_QUERY: Final[str] = 'Redrock/query'
USER_INFO_URL: Final[str] = 'OAuth2/UserInfo/__idaptive_cybr_user_oidc'


class ArkIdentityUsersService(ArkIdentityBaseService):
    def create_user(self, create_user: ArkIdentityCreateUser) -> ArkIdentityUser:
        """
        Creates a user with the given details, and returns its finalized details and id

        Args:
            create_user (ArkIdentityCreateUser): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkIdentityUser: _description_
        """
        self._logger.info(f'Creating identity user [{create_user.username}]')
        directories_service = ArkIdentityDirectoriesService(self._isp_auth)
        tenant_suffix = create_user.suffix or directories_service.tenant_default_suffix()
        response: Response = self._client.post(
            f'{self._url_prefix}{CREATE_USER_URL}',
            json={
                "DisplayName": create_user.display_name,
                "Name": f'{create_user.username}@{tenant_suffix}',
                "Mail": create_user.email,
                "Password": create_user.password.get_secret_value(),
                "MobileNumber": create_user.mobile_number,
                "InEverybodyRole": 'true',
                "InSysAdminRole": 'false',
                "ForcePasswordChangeNext": 'false',
                "SendEmailInvite": 'false',
                "SendSmsInvite": 'false',
            },
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to create user [{response.text}]')
            if create_user.roles:
                roles_service = ArkIdentityRolesService(self._isp_auth)
                for role in create_user.roles:
                    roles_service.add_user_to_role(
                        ArkIdentityAddUserToRole(username=f'{create_user.username}@{tenant_suffix}', role_name=role)
                    )
            self._logger.info(f'User created successfully with id [{result["Result"]}]')
            return ArkIdentityUser(
                user_id=result['Result'],
                username=f'{create_user.username}@{tenant_suffix}',
                display_name=create_user.display_name,
                email=create_user.email,
                mobile_number=create_user.mobile_number,
                roles=create_user.roles,
            )
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse create user response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse create user response [{str(ex)}]') from ex

    def update_user(self, update_user: ArkIdentityUpdateUser) -> None:
        """
        Updates the user information

        Args:
            update_user (ArkIdentityUpdateUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        if update_user.username and not update_user.user_id:
            update_user.user_id = self.user_id_by_name(ArkIdentityUserIdByName(username=update_user.username))
        self._logger.info(f'Updating identity user [{update_user.user_id}]')
        update_dict = {}
        if update_user.new_username:
            if '@' not in update_user.new_username:
                tenant_suffix = update_user.username.split('@')[1]
                update_user.new_username = f'{update_user.new_username}@{tenant_suffix}'
            update_dict['Name'] = update_user.new_username
        if update_user.display_name:
            update_dict['DisplayName'] = update_user.display_name
        if update_user.email:
            update_dict['Mail'] = update_user.email
        if update_user.mobile_number:
            update_dict['MobileNumber'] = update_user.mobile_number
        update_dict['ID'] = update_user.user_id
        response: Response = self._client.post(f'{self._url_prefix}{UPDATE_USER_URL}', json=update_dict)
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to update user [{response.text}]')
            self._logger.info('User updated successfully')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse update user response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse update user response [{str(ex)}]') from ex

    def delete_user(self, delete_user: ArkIdentityDeleteUser) -> None:
        """
        Deletes a user by given name

        Args:
            delete_user (ArkIdentityDeleteUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_user.username and not delete_user.user_id:
            delete_user.user_id = self.user_id_by_name(ArkIdentityUserIdByName(username=delete_user.username))
        self._logger.info(f'Deleting user [{delete_user.user_id}]')
        response: Response = self._client.post(f'{self._url_prefix}{DELETE_USER_URL}', json={'Users': [delete_user.user_id]})
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to delete user [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse delete user response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse delete user response [{str(ex)}]') from ex

    def user_id_by_name(self, user_id_by_name: ArkIdentityUserIdByName) -> str:
        """
        Finds the identifier of the given username

        Args:
            user_id_by_name (ArkIdentityUserIdByName): _description_

        Returns:
            str: _description_
        """
        response: Response = self._client.post(
            f'{self._url_prefix}{REDROCK_QUERY}',
            json={"Script": f"Select ID, Username from User WHERE Username='{user_id_by_name.username}'"},
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to retrieve user id by name [{response.text}] - [{response.status_code}]')
        try:
            query_result = response.json()
            if not query_result['success'] or len(query_result['Result']["Results"]) == 0:
                raise ArkServiceException('Failed to retrieve user id by name')
            return query_result['Result']["Results"][0]["Row"]["ID"]
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse user id by name response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse user id by name response [{str(ex)}]') from ex

    def user_by_name(self, user_id_by_name: ArkIdentityUserByName) -> ArkIdentityUser:
        """
        Finds the identifier of the given username

        Args:
            user_id_by_name (ArkIdentityUserIdByName): _description_

        Returns:
            str: _description_
        """
        response: Response = self._client.post(
            f'{self._url_prefix}{REDROCK_QUERY}',
            json={
                "Script": f"Select ID, Username, DisplayName, Email, MobileNumber, LastLogin from User WHERE Username='{user_id_by_name.username}'"
            },
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to retrieve user id by name [{response.text}] - [{response.status_code}]')
        try:
            query_result = response.json()
            if not query_result['success'] or len(query_result['Result']["Results"]) == 0:
                raise ArkServiceException('Failed to retrieve user id by name')
            user_row = query_result['Result']["Results"][0]["Row"]
            last_login = None
            if last_login := user_row.get('LastLogin'):
                try:
                    last_login = last_login.split('(')[1].split(')')[0]
                    last_login = f'{last_login[:10]}.{last_login[10:]}'  # for milliseconds
                    last_login = datetime.fromtimestamp(float(last_login), timezone.utc)
                except Exception as ex:
                    self._logger.debug(f'Failed to parse last login [{user_row.get("LastLogin")}] [{str(ex)}]')

            return ArkIdentityUser(
                user_id=user_row["ID"],
                username=user_row["Username"],
                display_name=user_row["DisplayName"],
                email=user_row["Email"],
                mobile_number=user_row["MobileNumber"],
                last_login=last_login,
            )
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse user id by name response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse user id by name response [{str(ex)}]') from ex

    def reset_user_password(self, reset_user_password: ArkIdentityResetUserPassword) -> None:
        """
        Resets a given username's password to the new given one
        Assumes the logged in user has permissions to do so

        Args:
            reset_user_password (ArkIdentityResetUserPassword): _description_

        Raises:
            ArkServiceException: _description_
        """
        user_id = self.user_id_by_name(ArkIdentityUserIdByName(username=reset_user_password.username))
        response: Response = self._client.post(
            f'{self._url_prefix}{RESET_USER_PASSWORD_URL}', json={'ID': user_id, 'newPassword': reset_user_password.new_password}
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to reset user password [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse reset user password response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse reset user password response [{str(ex)}]') from ex

    def user_info(self) -> ArkIdentityUserInfo:
        """
        Retrieves the current user info

        Raises:
            ArkServiceException: _description_
        """
        response: Response = self._client.post(
            f'{self._url_prefix}{USER_INFO_URL}',
            json={'Scopes': ['userInfo']},
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK:
                raise ArkServiceException(f'Failed to get user info [{response.text}]')
            return ArkIdentityUserInfo.parse_obj(result)
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to get user info [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to get user info [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
