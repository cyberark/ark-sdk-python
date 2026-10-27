from http import HTTPStatus
from typing import Final, Iterator, List, Optional, Set, Tuple

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.common import ArkPage
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.pcloud.usermgmt import (
    ArkPCloudActivateVaultUser,
    ArkPCloudAddVaultGroup,
    ArkPCloudAddVaultMemberToGroup,
    ArkPCloudAddVaultUser,
    ArkPCloudDeleteVaultGroup,
    ArkPCloudDeleteVaultUser,
    ArkPCloudDisableVaultUser,
    ArkPCloudEnableVaultUser,
    ArkPCloudGetVaultGroup,
    ArkPCloudGetVaultUser,
    ArkPCloudRemoveVaultMemberFromGroup,
    ArkPCloudUpdateVaultGroup,
    ArkPCloudUpdateVaultUser,
    ArkPCloudVaultAuthMethod,
    ArkPCloudVaultGroup,
    ArkPCloudVaultGroupsFilter,
    ArkPCloudVaultGroupsStats,
    ArkPCloudVaultUser,
    ArkPCloudVaultUsersFilter,
    ArkPCloudVaultUsersStats,
)
from ark_sdk_python.services.pcloud.common import ArkPCloudBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='pcloud-usermgmt', required_authenticator_names=[], optional_authenticator_names=['isp']
)
USERS_URL: Final[str] = 'users'
USER_URL: Final[str] = 'users/{user_id}'
GROUPS_URL: Final[str] = 'usergroups'
GROUP_URL: Final[str] = 'usergroups/{group_id}'
ADD_MEMBER_TO_GROUP_URL: Final[str] = 'usergroups/{group_id}/members'
REMOVE_MEMBER_FROM_GROUP_URL: Final[str] = 'usergroups/{group_id}/members/{member_id}'
ENABLE_USER: Final[str] = 'users/{user_id}/enable'
DISABLE_USER: Final[str] = 'users/{user_id}/disable'
ACTIVATE_USER: Final[str] = 'users/{user_id}/activate'
DEFAULT_USERS_PAGE_SIZE: Final[int] = 200

ArkPCloudVaultUsersPage = ArkPage[ArkPCloudVaultUser]


class ArkPCloudUserMgmtService(ArkPCloudBaseService):
    def __list_vault_users_page(
        self, vault_users_filters: ArkPCloudVaultUsersFilter, page_offset: int, page_size: int
    ) -> Tuple[List[ArkPCloudVaultUser], Optional[int]]:
        """One page of the vault users (pageOffset / pageSize), with the total of the matching users when the vault returns it"""
        args = {'ExtendedDetails': vault_users_filters.extended_details, 'pageOffset': page_offset, 'pageSize': page_size}
        if vault_users_filters.search:
            args['search'] = vault_users_filters.search
        if vault_users_filters.sort:
            args['sort'] = vault_users_filters.sort
        conditions = []
        if vault_users_filters.user_type:
            conditions.append(f'userType eq {vault_users_filters.user_type}')
        if vault_users_filters.component_user is not None:
            conditions.append(f'componentUser eq {str(vault_users_filters.component_user).lower()}')
        if vault_users_filters.user_name:
            conditions.append(f'userName eq {vault_users_filters.user_name}')
        if conditions:
            args['filter'] = ' AND '.join(conditions)
        resp: Response = self._client.get(USERS_URL, params=args)
        if resp.status_code == HTTPStatus.OK:
            try:
                body = resp.json()
                return TypeAdapter(List[ArkPCloudVaultUser]).validate_python(body['Users']), body.get('Total')
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list vault users response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list vault users response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list vault users [{resp.text}] - [{resp.status_code}]')

    def __list_vault_groups_with_filters(
        self, search: Optional[str] = None, sort: Optional[str] = None, group_type: Optional[str] = None, group_name: Optional[str] = None
    ) -> List[ArkPCloudVaultGroup]:
        args = {'includeMembers': True}
        vault_groups_filter = ''
        if search:
            args['search'] = search
        if sort:
            args['sort'] = sort
        if group_type:
            vault_groups_filter = f'groupType eq {group_type}'
        if group_name:
            if vault_groups_filter:
                vault_groups_filter += ' AND '
            vault_groups_filter += f'groupName eq {group_name}'
        if vault_groups_filter:
            args['filter'] = vault_groups_filter
        resp: Response = self._client.get(GROUPS_URL, params=args)
        if resp.status_code == HTTPStatus.OK:
            try:
                return TypeAdapter(List[ArkPCloudVaultGroup]).validate_python(resp.json()['value'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list vault groups response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list vault groups response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list vault groups [{resp.text}] - [{resp.status_code}]')

    def list_vault_users_pages(self, vault_users_filters: Optional[ArkPCloudVaultUsersFilter] = None) -> Iterator[ArkPCloudVaultUsersPage]:
        """
        Lists the vault users in pages (pageOffset / pageSize), so a big vault is read in small calls instead of one that may time out.
        The listing starts at `page_offset` (to resume), asks `page_size` users per call, and ends on an empty page. A vault that
        ignores the paging parameters and returns the same users again is detected and ends the listing.
        https://docs.cyberark.com/pam-self-hosted/latest/en/content/sdk/get-users-api.htm

        Args:
            vault_users_filters (Optional[ArkPCloudVaultUsersFilter], optional): filters and paging, all the users when not given

        Yields:
            Iterator[ArkPCloudVaultUsersPage]: pages of the vault users
        """
        filters = vault_users_filters or ArkPCloudVaultUsersFilter()
        page_size = filters.page_size or DEFAULT_USERS_PAGE_SIZE
        offset = filters.page_offset or 0
        seen_ids: Set[int] = set()
        self._logger.info(f'Listing vault users with filters [{filters}] in pages of [{page_size}]')
        while True:
            users, total = self.__list_vault_users_page(filters, offset, page_size)
            new_users = [user for user in users if user.id not in seen_ids]
            if not new_users:
                return
            seen_ids.update(user.id for user in new_users)
            offset += len(users)
            yield ArkPCloudVaultUsersPage(items=new_users)
            if total is not None and offset >= total and len(users) < page_size:
                return

    def list_vault_users(self) -> List[ArkPCloudVaultUser]:
        """
        Lists all vault users visible to the logged in user, read in pages
        https://docs.cyberark.com/pam-self-hosted/latest/en/content/sdk/get-users-api.htm

        Returns:
            List[ArkPCloudVaultUser]: _description_
        """
        self._logger.info('Listing all vault users')
        return [user for page in self.list_vault_users_pages() for user in page.items]

    def list_vault_users_by(self, vault_users_filters: ArkPCloudVaultUsersFilter) -> List[ArkPCloudVaultUser]:
        """
        Lists vault users by given filters, read in pages
        https://docs.cyberark.com/pam-self-hosted/latest/en/content/sdk/get-users-api.htm

        Args:
            vault_users_filters (ArkPCloudVaultUsersFilter): _description_

        Returns:
            List[ArkPCloudVaultUser]: _description_
        """
        self._logger.info(f'Listing vault users with filters [{vault_users_filters}]')
        return [user for page in self.list_vault_users_pages(vault_users_filters) for user in page.items]

    def list_vault_groups(self) -> List[ArkPCloudVaultGroup]:
        """
        Listing all vault groups visible to the user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/GetGroupsFromVault.htm

        Returns:
            List[ArkPCloudVaultGroup]: _description_
        """
        self._logger.info('Listing all vault groups')
        return self.__list_vault_groups_with_filters()

    def list_vault_groups_by(self, vault_groups_filter: ArkPCloudVaultGroupsFilter) -> List[ArkPCloudAddVaultGroup]:
        """
        Lists vault groups by given filters
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/GetGroupsFromVault.htm

        Args:
            vault_groups_filter (ArkPCloudVaultGroupsFilter): _description_

        Returns:
            List[ArkPCloudAddVaultGroup]: _description_
        """
        self._logger.info(f'Listing vault groups with filters [{vault_groups_filter}]')
        return self.__list_vault_groups_with_filters(
            vault_groups_filter.search, vault_groups_filter.sort, vault_groups_filter.group_type, vault_groups_filter.group_name
        )

    def add_vault_user(self, add_vault_user: ArkPCloudAddVaultUser) -> ArkPCloudVaultUser:
        """
        Adds a new vault user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/API-AddUser-v10.htm

        Args:
            add_vault_user (ArkPCloudAddVaultUser): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultUser: _description_
        """
        self._logger.info('Adding new vault user')
        resp: Response = self._client.post(USERS_URL, json=add_vault_user.model_dump(by_alias=True, exclude_none=True))
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkPCloudVaultUser.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add vault user response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add vault user response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add vault user [{resp.text}] - [{resp.status_code}]')

    def add_vault_group(self, add_vault_group: ArkPCloudAddVaultGroup) -> ArkPCloudVaultGroup:
        """
        Adds a new vault group
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/rest-api-create-group.htm

        Args:
            add_vault_group (ArkPCloudAddVaultGroup): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultGroup: _description_
        """
        self._logger.info('Adding new vault group')
        resp: Response = self._client.post(GROUPS_URL, json=add_vault_group.model_dump(by_alias=True, exclude_none=True))
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkPCloudVaultGroup.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add vault group response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add vault group response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add vault group [{resp.text}] - [{resp.status_code}]')

    def add_vault_member_to_group(self, add_vault_member_to_group: ArkPCloudAddVaultMemberToGroup) -> ArkPCloudVaultGroup:
        """
        Adds a new member to a vault group
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/AddMemberToGroup%20v10.htm

        Args:
            add_vault_member_to_group (ArkPCloudAddVaultMemberToGroup): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultGroup: _description_
        """
        self._logger.info(f'Adding member [{add_vault_member_to_group.member_id}] to group [{add_vault_member_to_group.group_id}]')
        resp: Response = self._client.post(
            ADD_MEMBER_TO_GROUP_URL.format(group_id=add_vault_member_to_group.group_id),
            json=add_vault_member_to_group.model_dump(by_alias=True, exclude_none=True, exclude={'group_id'}),
        )
        if resp.status_code == HTTPStatus.CREATED:
            return self.vault_group(ArkPCloudGetVaultGroup(group_id=add_vault_member_to_group.group_id))
        raise ArkServiceException(f'Failed to add vault member to group [{resp.text}] - [{resp.status_code}]')

    def delete_vault_user(self, delete_vault_user: ArkPCloudDeleteVaultUser) -> None:
        """
        Deletes a vault user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Users%20Web%20Services%20-%20Delete%20User.htm

        Args:
            delete_vault_user (ArkPCloudDeleteVaultUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting vault user [{delete_vault_user.user_id}]')
        resp: Response = self._client.delete(USER_URL.format(user_id=delete_vault_user.user_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete vault user [{resp.text}] - [{resp.status_code}]')

    def delete_vault_group(self, delete_vault_group: ArkPCloudDeleteVaultGroup) -> None:
        """
        Deletes a vault group
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Users%20Web%20Services%20-%20Delete%20User%20Group.htm

        Args:
            delete_vault_group (ArkPCloudDeleteVaultGroup): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting vault group [{delete_vault_group.group_id}]')
        resp: Response = self._client.delete(GROUP_URL.format(group_id=delete_vault_group.group_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete vault group [{resp.text}] - [{resp.status_code}]')

    def remove_vault_member_from_group(self, remove_vault_member_from_group: ArkPCloudRemoveVaultMemberFromGroup) -> ArkPCloudVaultGroup:
        """
        Removes a member from a vault group
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/RemoveUserFromGroup.htm

        Args:
            remove_vault_member_from_group (ArkPCloudRemoveVaultMemberFromGroup): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultGroup: _description_
        """
        self._logger.info(
            f'Removing member [{remove_vault_member_from_group.member_id}] from group [{remove_vault_member_from_group.group_id}]'
        )
        resp: Response = self._client.delete(
            REMOVE_MEMBER_FROM_GROUP_URL.format(
                group_id=remove_vault_member_from_group.group_id, member_id=remove_vault_member_from_group.member_id
            )
        )
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return self.vault_group(ArkPCloudGetVaultGroup(group_id=remove_vault_member_from_group.group_id))
        raise ArkServiceException(f'Failed to remove vault member from group [{resp.text}] - [{resp.status_code}]')

    def update_vault_user(self, update_vault_user: ArkPCloudUpdateVaultUser) -> ArkPCloudVaultUser:
        """
        Updates a vault user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Users%20Web%20Services%20-%20Update%20User.htm

        Args:
            update_vault_user (ArkPCloudUpdateVaultUser): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultUser: _description_
        """
        self._logger.info(f'Updating vault user [{update_vault_user.user_id}]')
        resp: Response = self._client.put(
            USER_URL.format(user_id=update_vault_user.user_id),
            json=update_vault_user.model_dump(by_alias=True, exclude_none=True, exclude={'user_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudVaultUser.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update vault user response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update vault user response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update vault user [{resp.text}] - [{resp.status_code}]')

    def update_vault_group(self, update_vault_group: ArkPCloudUpdateVaultGroup) -> ArkPCloudVaultGroup:
        """
        Updates a vault group
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Update-group.htm

        Args:
            update_vault_group (ArkPCloudUpdateVaultGroup): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultGroup: _description_
        """
        self._logger.info(f'Updating vault group [{update_vault_group.group_id}]')
        resp: Response = self._client.put(
            GROUP_URL.format(group_id=update_vault_group.group_id),
            json=update_vault_group.model_dump(by_alias=True, exclude_none=True, exclude={'group_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudVaultGroup.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update vault group response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update vault group response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update vault group [{resp.text}] - [{resp.status_code}]')

    def vault_user(self, get_vault_user: ArkPCloudGetVaultUser) -> ArkPCloudVaultUser:
        """
        Retrieves a vault user by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/get-user-details-v10.htm

        Args:
            get_vault_user (ArkPCloudGetVaultUser): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultUser: _description_
        """
        self._logger.info(f'Retrieving vault user [{get_vault_user.user_id}]')
        resp: Response = self._client.get(USER_URL.format(user_id=get_vault_user.user_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudVaultUser.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse vault user response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse vault user response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve vault user [{resp.text}] - [{resp.status_code}]')

    def vault_group(self, get_vault_group: ArkPCloudGetVaultGroup) -> ArkPCloudVaultGroup:
        """
        Retrieves a vault group by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/GetGroupDetails.htm

        Args:
            get_vault_group (ArkPCloudGetVaultGroup): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudVaultGroup: _description_
        """
        self._logger.info(f'Retrieving vault group [{get_vault_group.group_id}]')
        resp: Response = self._client.get(GROUP_URL.format(group_id=get_vault_group.group_id) + '?includeMembers=true')
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudVaultGroup.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse vault group response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse vault group response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve vault group [{resp.text}] - [{resp.status_code}]')

    def enable_vault_user(self, enable_vault_user: ArkPCloudEnableVaultUser) -> None:
        """
        Enables the vault user to be used
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Enable-user.htm

        Args:
            enable_vault_user (ArkPCloudEnableVaultUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Enabling vault user [{enable_vault_user.user_id}]')
        resp: Response = self._client.post(ENABLE_USER.format(user_id=enable_vault_user.user_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to enable vault user [{resp.text}] - [{resp.status_code}]')

    def disable_vault_user(self, disable_vault_user: ArkPCloudDisableVaultUser) -> None:
        """
        Disables the vault user from being used
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Disable-user.htm

        Args:
            disable_vault_user (ArkPCloudDisableVaultUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Disabling vault user [{disable_vault_user.user_id}]')
        resp: Response = self._client.post(DISABLE_USER.format(user_id=disable_vault_user.user_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to disable vault user [{resp.text}] - [{resp.status_code}]')

    def activate_vault_user(self, activate_vault_user: ArkPCloudActivateVaultUser) -> None:
        """
        Activates a locked vault user who failed logging in and was suspended
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/activate-user-v10.htm

        Args:
            activate_vault_user (ArkPCloudActivateVaultUser): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Activating vault user [{activate_vault_user.user_id}]')
        resp: Response = self._client.post(ACTIVATE_USER.format(user_id=activate_vault_user.user_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to activate vault user [{resp.text}] - [{resp.status_code}]')

    def vault_users_stats(self) -> ArkPCloudVaultUsersStats:
        """
        Calculates vault users stats

        Returns:
            ArkPCloudVaultUsersStats: _description_
        """
        self._logger.info('Calculating vault users statistics')
        vault_users = self.list_vault_users()
        vault_users_stats = ArkPCloudVaultUsersStats.model_construct()
        vault_users_stats.users_count = len(vault_users)

        # Get auth methods count per user
        auth_methods: Set[ArkPCloudVaultAuthMethod] = {vu.authentication_method for vu in vault_users}
        vault_users_stats.users_auth_methods_count = {
            am: len([vu for vu in vault_users if vu.authentication_method == am]) for am in auth_methods
        }

        # Get user types count per user
        user_types: Set[str] = {vu.user_type for vu in vault_users}
        vault_users_stats.users_types_count = {ut: len([vu for vu in vault_users if vu.user_type == ut]) for ut in user_types}

        return vault_users_stats

    def vault_groups_stats(self) -> ArkPCloudVaultGroupsStats:
        """
        Calculates vault groups stats

        Returns:
            ArkPCloudVaultGroupsStats: _description_
        """
        self._logger.info('Calculating vault groups statistics')
        vault_groups = self.list_vault_groups()
        vault_groups_stats = ArkPCloudVaultGroupsStats.model_construct()
        vault_groups_stats.groups_count = len(vault_groups)

        # Get group types count per group
        group_types: Set[str] = {vg.group_type for vg in vault_groups}
        vault_groups_stats.group_types_count = {gt: len([vg for vg in vault_groups if vg.group_type == gt]) for gt in group_types}

        return vault_groups_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
