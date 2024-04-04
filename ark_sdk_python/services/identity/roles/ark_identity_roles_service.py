from http import HTTPStatus
from typing import Final, List

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.common.identity import (
    DirectorySearchArgs,
    DirectoryService,
    DirectoryServiceQueryResponse,
    DirectoryServiceQuerySpecificRoleRequest,
)
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.directories import ArkIdentityEntityType, ArkIdentityListDirectories
from ark_sdk_python.models.services.identity.roles import (
    ArkIdentityAddAdminRightsToRole,
    ArkIdentityAddGroupToRole,
    ArkIdentityAddRoleToRole,
    ArkIdentityAddUserToRole,
    ArkIdentityCreateRole,
    ArkIdentityDeleteRole,
    ArkIdentityListRoleMembers,
    ArkIdentityRemoveGroupFromRole,
    ArkIdentityRemoveRoleFromRole,
    ArkIdentityRemoveUserFromRole,
    ArkIdentityRole,
    ArkIdentityRoleIdByName,
    ArkIdentityRoleMember,
    ArkIdentityUpdateRole,
)
from ark_sdk_python.services.identity.common import ArkIdentityBaseService
from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-roles', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

ADD_USER_TO_ROLE_URL: Final[str] = 'SaasManage/AddUsersAndGroupsToRole'
CREATE_ROLE_URL: Final[str] = 'Roles/StoreRole'
UPDATE_ROLE_URL: Final[str] = 'Roles/UpdateRole'
ROLE_MEMBERS_URL: Final[str] = 'Roles/GetRoleMembers'
ADD_ADMIN_RIGHTS_TO_ROLE_URL: Final[str] = 'SaasManage/AssignSuperRights'
REMOVE_USER_FROM_ROLE_URL: Final[str] = 'SaasManage/RemoveUsersAndGroupsFromRole'
DELETE_ROLE_URL: Final[str] = 'SaasManage/DeleteRole'
DIRECTORY_SERVICE_QUERY_URL: Final[str] = 'UserMgmt/DirectoryServiceQuery'
REDROCK_QUERY: Final[str] = 'Redrock/query'


class ArkIdentityRolesService(ArkIdentityBaseService):
    def create_role(self, create_role: ArkIdentityCreateRole) -> ArkIdentityRole:
        """
        Creates a role by given name and adds admin rights to it
        If the role exists, will only alter admin rights and return it

        Args:
            create_role (ArkIdentityCreateRole): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkIdentityRole: _description_
        """
        role_details = None
        self._logger.info(f'Trying to create role [{create_role.role_name}]')
        try:
            # Role exists
            role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=create_role.role_name))
            role_details = ArkIdentityRole(role_name=create_role.role_name, role_id=role_id)
            self._logger.info(f'Role already exists with id [{role_id}]')
        except (ValidationError, Exception) as ex:
            # Create the role
            create_dict = {'Name': create_role.role_name}
            if create_role.description:
                create_dict['Description'] = create_role.description
            response: Response = self._client.post(f'{self._url_prefix}{CREATE_ROLE_URL}', json=create_dict)
            try:
                result = response.json()
                if response.status_code != HTTPStatus.OK or not result['success']:
                    raise ArkServiceException(f'Failed to create role [{response.text}]') from ex
                role_id = result['Result']['_RowKey']
                role_details = ArkIdentityRole(role_name=create_role.role_name, role_id=role_id)
                self._logger.info(f'Role created with id [{role_id}]')
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse create role response [{str(ex)}] - [{response.text}]')
                raise ArkServiceException(f'Failed to parse create role response [{str(ex)}]') from ex
        # Add admin rights
        if create_role.admin_rights:
            self.add_admin_rights_to_role(
                ArkIdentityAddAdminRightsToRole(role_id=role_details.role_id, admin_rights=create_role.admin_rights)
            )
        return role_details

    def update_role(self, update_role: ArkIdentityUpdateRole) -> None:
        """
        Updates a role details

        Args:
            update_role (ArkIdentityUpdateRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        if update_role.role_name and not update_role.role_id:
            update_role.role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=update_role.role_name))
        self._logger.info(f'Updating identity role [{update_role.role_id}]')
        update_dict = {'Name': update_role.role_id}
        if update_role.new_role_name:
            update_dict['NewName'] = update_role.new_role_name
        if update_role.description:
            update_role['Description'] = update_role.description
        response: Response = self._client.post(f'{self._url_prefix}{UPDATE_ROLE_URL}', json=update_dict)
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to update role [{response.text}]')
            self._logger.info('Role updated successfully')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse update role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse update role response [{str(ex)}]') from ex

    def list_role_members(self, list_role_members: ArkIdentityListRoleMembers) -> List[ArkIdentityRoleMember]:
        """
        Lists a role members

        Args:
            list_role_members (ArkIdentityListRoleMembers): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkIdentityRoleMember]: _description_
        """
        if list_role_members.role_name and not list_role_members.role_id:
            list_role_members.role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=list_role_members.role_name))
        self._logger.info(f'Listing identity role [{list_role_members.role_id}] members')
        response: Response = self._client.post(f'{self._url_prefix}{ROLE_MEMBERS_URL}', json={'Name': list_role_members.role_id})
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to list role members [{response.text}]')
            members = []
            if 'Result' in result and 'Results' in result['Result'] and len(result['Result']['Results']) > 0:
                members = [
                    ArkIdentityRoleMember(
                        member_id=r['Row']['Guid'],
                        member_name=r['Row']['Name'],
                        member_type=ArkIdentityEntityType(r['Row']['Type'].upper()),
                    )
                    for r in result['Result']['Results']
                ]
            self._logger.info('Listed role members successfully successfully')
            return members
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse list role members response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse list role members response [{str(ex)}]') from ex

    def add_admin_rights_to_role(self, add_admin_rights_to_role: ArkIdentityAddAdminRightsToRole) -> None:
        """
        Adds given admin rights to the role assuming it exists

        Args:
            add_admin_rights_to_role (ArkIdentityAddAdminRightsToRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding admin rights [{add_admin_rights_to_role.admin_rights}] to role [{add_admin_rights_to_role.role_name}]')
        if not add_admin_rights_to_role.role_id and not add_admin_rights_to_role.role_name:
            raise ArkServiceException('Either role id or role name must be given')
        if add_admin_rights_to_role.role_id:
            role_id = add_admin_rights_to_role.role_id
        else:
            role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=add_admin_rights_to_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{ADD_ADMIN_RIGHTS_TO_ROLE_URL}',
            json=[{'Role': role_id, 'Path': admin_right.value} for admin_right in add_admin_rights_to_role.admin_rights],
        )
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to add admin rights to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add admin rights to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add admin rights to role response [{str(ex)}]') from ex

    def role_id_by_name(self, role_id_by_name: ArkIdentityRoleIdByName) -> str:
        """
        For a given role name, find its identifier on identity

        Args:
            role_id_by_name (ArkIdentityRoleIdByName): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: _description_
        """
        self._logger.info(f'Retrieving role id for name [{role_id_by_name.role_name}]')
        directories_service = ArkIdentityDirectoriesService(self._isp_auth)
        directories = [
            d.directory_service_uuid
            for d in directories_service.list_directories(ArkIdentityListDirectories(directories=[DirectoryService.Identity]))
        ]
        response: Response = self._client.post(
            f'{self._url_prefix}{DIRECTORY_SERVICE_QUERY_URL}',
            data=DirectoryServiceQuerySpecificRoleRequest(
                role_name=role_id_by_name.role_name, directory_services=directories, args=DirectorySearchArgs(limit=1)
            ).json(by_alias=True, exclude={'users'}),
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to query for directory services role [{response.text}]')
        try:
            result = DirectoryServiceQueryResponse.parse_raw(response.text)
            all_roles = result.result.roles.results
            if not len(all_roles):
                raise ArkServiceException('No role found for given name')
            return all_roles[0].row.id
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to parse role id by name response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse role id by name response [{str(ex)}]') from ex

    def add_user_to_role(self, add_user_to_role: ArkIdentityAddUserToRole) -> None:
        """
        Adds a given user to the role

        Args:
            add_user_to_role (ArkIdentityAddUserToRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding user [{add_user_to_role.username}] to role [{add_user_to_role.role_name}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=add_user_to_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{ADD_USER_TO_ROLE_URL}',
            json={
                'Name': role_id,
                'Users': [add_user_to_role.username],
            },
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to add user to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add user to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add user to role response [{str(ex)}]') from ex

    def add_group_to_role(self, add_group_to_role: ArkIdentityAddGroupToRole) -> None:
        """
        Adds a given group to the role

        Args:
            add_group_to_role (ArkIdentityAddGroupToRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding group [{add_group_to_role.group_name}] to role [{add_group_to_role.role_name}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=add_group_to_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{ADD_USER_TO_ROLE_URL}',
            json={
                'Name': role_id,
                'Groups': [add_group_to_role.group_name],
            },
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to add group to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add group to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add group to role response [{str(ex)}]') from ex

    def add_role_to_role(self, add_role_to_role: ArkIdentityAddRoleToRole) -> None:
        """
        Adds a given group to the role

        Args:
            add_role_to_role (ArkIdentityAddRoleToRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding role [{add_role_to_role.role_name_to_add}] to role [{add_role_to_role.role_name}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=add_role_to_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{ADD_USER_TO_ROLE_URL}',
            json={
                'Name': role_id,
                'Roles': [add_role_to_role.role_name_to_add],
            },
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to add role to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add role to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add role to role response [{str(ex)}]') from ex

    def remove_user_from_role(self, remove_user_from_role: ArkIdentityRemoveUserFromRole) -> None:
        """
        Removes a given user from the given role

        Args:
            remove_user_from_role (ArkIdentityRemoveUserFromRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Removing user [{remove_user_from_role.username}] from role [{remove_user_from_role.role_name}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=remove_user_from_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{REMOVE_USER_FROM_ROLE_URL}', json={'Name': role_id, 'Users': [remove_user_from_role.username]}
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to remove user to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse remove user to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse remove user to role response [{str(ex)}]') from ex

    def remove_group_from_role(self, remove_group_from_role: ArkIdentityRemoveGroupFromRole) -> None:
        """
        Removes a given group from the given role

        Args:
            remove_group_from_role (ArkIdentityRemoveGroupFromRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Removing group [{remove_group_from_role.group_name}] from role [{remove_group_from_role.role_name}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=remove_group_from_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{REMOVE_USER_FROM_ROLE_URL}', json={'Name': role_id, 'Groups': [remove_group_from_role.group_name]}
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to remove group to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse remove group to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse remove group to role response [{str(ex)}]') from ex

    def remove_role_from_role(self, remove_role_from_role: ArkIdentityRemoveRoleFromRole) -> None:
        """
        Removes a given role from the given role

        Args:
            remove_role_from_role (ArkIdentityRemoveRoleFromRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Removing group [{remove_role_from_role.role_name}] from role [{remove_role_from_role.role_name_to_remove}]')
        role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=remove_role_from_role.role_name))
        response: Response = self._client.post(
            f'{self._url_prefix}{REMOVE_USER_FROM_ROLE_URL}', json={'Name': role_id, 'Roles': [remove_role_from_role.role_name_to_remove]}
        )
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to remove role to role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse remove role to role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse remove role to role response [{str(ex)}]') from ex

    def delete_role(self, delete_role: ArkIdentityDeleteRole) -> None:
        """
        Deletes a given role by name

        Args:
            delete_role (ArkIdentityDeleteRole): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting role [{delete_role.role_name}]')
        if delete_role.role_name and not delete_role.role_id:
            delete_role.role_id = self.role_id_by_name(ArkIdentityRoleIdByName(role_name=delete_role.role_name))
        response: Response = self._client.post(f'{self._url_prefix}{DELETE_ROLE_URL}', json={'Name': delete_role.role_id})
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to delete role [{response.text}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse delete role response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse delete role response [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
