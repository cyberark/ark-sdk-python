import itertools
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from typing import Dict, Final, Iterator, List, Optional, Set
from urllib.parse import parse_qs, urlparse

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.common import ArkPage
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkCountedValues
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.pcloud.safes import (
    ArkPCloudAddSafe,
    ArkPCloudAddSafeMember,
    ArkPCloudDeleteSafe,
    ArkPCloudDeleteSafeMember,
    ArkPCloudGetSafe,
    ArkPCloudGetSafeMember,
    ArkPCloudGetSafeMembersStats,
    ArkPCloudListSafeMembers,
    ArkPCloudSafe,
    ArkPCloudSafeMember,
    ArkPCloudSafeMemberPermissions,
    ArkPCloudSafeMemberPermissionSet,
    ArkPCloudSafeMembersFilters,
    ArkPCloudSafeMembersStats,
    ArkPCloudSafeMemberType,
    ArkPCloudSafesFilters,
    ArkPCloudSafesMembersStats,
    ArkPCloudSafesStats,
    ArkPCloudUpdateSafe,
    ArkPCloudUpdateSafeMember,
)
from ark_sdk_python.services.pcloud.common import ArkPCloudBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='pcloud-safes', required_authenticator_names=[], optional_authenticator_names=['isp']
)
SAFES_URL: Final[str] = 'safes'
SAFE_URL: Final[str] = 'safes/{safe_id}'
SAFE_MEMBERS_URL: Final[str] = 'safes/{safe_id}/members'
SAFE_MEMBER_URL: Final[str] = 'safes/{safe_id}/members/{member_name}'
SAFE_MEMBER_PERMISSIONS_SETS: Final[Dict[ArkPCloudSafeMemberPermissionSet, ArkPCloudSafeMemberPermissions]] = {
    ArkPCloudSafeMemberPermissionSet.ConnectOnly: ArkPCloudSafeMemberPermissions(list_accounts=True, use_accounts=True),
    ArkPCloudSafeMemberPermissionSet.ReadOnly: ArkPCloudSafeMemberPermissions(
        list_accounts=True, use_accounts=True, retrieve_accounts=True
    ),
    ArkPCloudSafeMemberPermissionSet.Approver: ArkPCloudSafeMemberPermissions(
        list_accounts=True, view_safe_members=True, manage_safe_members=True, requests_authorization_level1=True
    ),
    ArkPCloudSafeMemberPermissionSet.AccountsManager: ArkPCloudSafeMemberPermissions(
        list_accounts=True,
        use_accounts=True,
        retrieve_accounts=True,
        add_accounts=True,
        update_account_properties=True,
        update_account_content=True,
        initiate_cpm_account_management_operations=True,
        specify_next_account_content=True,
        rename_accounts=True,
        delete_accounts=True,
        unlock_accounts=True,
        view_safe_members=True,
        manage_safe_members=True,
        view_audit_log=True,
        access_without_confirmation=True,
    ),
    ArkPCloudSafeMemberPermissionSet.Full: ArkPCloudSafeMemberPermissions(
        list_accounts=True,
        use_accounts=True,
        retrieve_accounts=True,
        add_accounts=True,
        update_account_properties=True,
        update_account_content=True,
        initiate_cpm_account_management_operations=True,
        specify_next_account_content=True,
        rename_accounts=True,
        delete_accounts=True,
        unlock_accounts=True,
        view_safe_members=True,
        manage_safe_members=True,
        view_audit_log=True,
        access_without_confirmation=True,
        requests_authorization_level1=True,
        manage_safe=True,
        backup_safe=True,
        move_accounts_and_folders=True,
        create_folders=True,
        delete_folders=True,
    ),
}

ArkPCloudSafesPage = ArkPage[ArkPCloudSafe]
ArkPCloudSafeMembersPage = ArkPage[ArkPCloudSafeMember]


class ArkPCloudSafesService(ArkPCloudBaseService):
    def __list_safes_with_filters(
        self, search: Optional[str] = None, sort: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> Iterator[ArkPCloudSafesPage]:
        query = {}
        if search:
            query['search'] = search
        if sort:
            query['sort'] = sort
        if offset:
            query['offset'] = offset
        if limit:
            query['limit'] = limit
        while True:
            resp: Response = self._client.get(SAFES_URL, params=query)
            if resp.status_code == HTTPStatus.OK:
                try:
                    result = resp.json()
                    safes = None
                    if 'value' in result:
                        safes = result['value']
                    elif 'Safes' in result:
                        safes = result['Safes']
                    if not safes:
                        raise ArkServiceException('Failed to list safes, unexpected result')
                    safes = [{f'{k[0].lower()}{k[1:]}': v for k, v in safe.items()} for safe in safes]
                    accounts = TypeAdapter(List[ArkPCloudSafe]).validate_python(safes)
                    yield ArkPCloudSafesPage(items=accounts)
                    if 'nextLink' in result:
                        query = parse_qs(urlparse(result['nextLink']).query)
                    else:
                        break
                except (ValidationError, JSONDecodeError, KeyError) as ex:
                    self._logger.exception(f'Failed to parse list safes response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list safes response [{str(ex)}]') from ex
            else:
                raise ArkServiceException(f'Failed to list safes [{resp.text}] - [{resp.status_code}]')

    def __list_safe_members_with_filters(
        self,
        safe_id: str,
        search: Optional[str] = None,
        sort: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        member_type: Optional[ArkPCloudSafeMemberType] = None,
    ) -> Iterator[ArkPCloudSafeMembersPage]:
        query = {}
        if search:
            query['search'] = search
        if sort:
            query['sort'] = sort
        if offset:
            query['offset'] = offset
        if limit:
            query['limit'] = limit
        if member_type:
            query['filter'] = f'memberType eq {member_type.value}'
        while True:
            resp: Response = self._client.get(SAFE_MEMBERS_URL.format(safe_id=safe_id), params=query)
            if resp.status_code == HTTPStatus.OK:
                try:
                    result = resp.json()
                    safe_members = TypeAdapter(List[ArkPCloudSafeMember]).validate_python(result['value'])
                    for sm in safe_members:
                        sm.permission_set = (
                            [p for p in SAFE_MEMBER_PERMISSIONS_SETS.keys() if SAFE_MEMBER_PERMISSIONS_SETS[p] == sm.permissions]
                            + [ArkPCloudSafeMemberPermissionSet.Custom]
                        )[0]
                    yield ArkPCloudSafeMembersPage(items=safe_members)
                    if 'nextLink' in result:
                        query = parse_qs(urlparse(result['nextLink']).query)
                    else:
                        break
                except (ValidationError, JSONDecodeError, KeyError) as ex:
                    self._logger.exception(f'Failed to parse list safe members response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list safe members response [{str(ex)}]') from ex
            else:
                raise ArkServiceException(f'Failed to list safe members [{resp.text}] - [{resp.status_code}]')

    def list_safes(self) -> Iterator[ArkPCloudSafesPage]:
        """
        Lists all the visible safes of the logged in user as pages of safes
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safes%20Web%20Services%20-%20List%20Safes.htm?

        Yields:
            Iterator[ArkPCloudSafesPage]: _description_
        """
        self._logger.info('Listing all safes')
        yield from self.__list_safes_with_filters()

    def list_safes_by(self, safes_filter: ArkPCloudSafesFilters) -> Iterator[ArkPCloudSafesPage]:
        """
        Lists the visible safes of the logged in user by filters as pages of safes
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safes%20Web%20Services%20-%20List%20Safes.htm?

        Yields:
            Iterator[ArkPCloudSafesPage]: _description_
        """
        self._logger.info(f'Listing safes by filter [{safes_filter}]')
        yield from self.__list_safes_with_filters(safes_filter.search, safes_filter.sort, safes_filter.offset, safes_filter.limit)

    def list_safe_members(self, list_safe_members: ArkPCloudListSafeMembers) -> Iterator[ArkPCloudSafeMembersPage]:
        """
        Lists all safe mmebers of a given safe that are visible to the logged in user as pages of safe members
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safe%20Members%20WS%20-%20List%20Safe%20Members.htm

        Args:
            list_safe_members (ArkPCloudListSafeMembers): _description_

        Yields:
            Iterator[ArkPCloudSafeMembersPage]: _description_
        """
        self._logger.info('Listing all safe members')
        yield from self.__list_safe_members_with_filters(list_safe_members.safe_id)

    def list_safe_members_by(self, safe_members_filter: ArkPCloudSafeMembersFilters) -> Iterator[ArkPCloudSafeMembersPage]:
        """
        Lists safe mmebers of a given safe that are visible to the logged in user by filters as pages of safe members
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safe%20Members%20WS%20-%20List%20Safe%20Members.htm

        Args:
            safe_members_filter (ArkPCloudSafeMembersFilters): _description_

        Yields:
            Iterator[ArkPCloudSafeMembersPage]: _description_
        """
        self._logger.info(f'Listing safe members by filter [{safe_members_filter}]')
        yield from self.__list_safe_members_with_filters(
            safe_members_filter.safe_id,
            safe_members_filter.search,
            safe_members_filter.sort,
            safe_members_filter.offset,
            safe_members_filter.limit,
            safe_members_filter.member_type,
        )

    def safe(self, get_safe: ArkPCloudGetSafe) -> ArkPCloudSafe:
        """
        Retrieves a safe by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safes%20Web%20Services%20-%20Get%20Safes%20Details.htm

        Args:
            get_safe (ArkPCloudGetSafe): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafe: _description_
        """
        self._logger.info(f'Retrieving safe by id [{get_safe.safe_id}]')
        resp: Response = self._client.get(SAFE_URL.format(safe_id=get_safe.safe_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudSafe.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse safe response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse safe response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve safe [{resp.text}] - [{resp.status_code}]')

    def safe_member(self, get_safe_member: ArkPCloudGetSafeMember) -> ArkPCloudSafeMember:
        """
        Retrieves a safe member by safe id and member name
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Safe%20Members%20WS%20-%20List%20Safe%20Member.htm

        Args:
            get_safe_member (ArkPCloudGetSafeMember): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafeMember: _description_
        """
        self._logger.info(f'Retrieving safe member by safe [{get_safe_member.safe_id}] and member name [{get_safe_member.member_name}]')
        resp: Response = self._client.get(SAFE_MEMBER_URL.format(safe_id=get_safe_member.safe_id, member_name=get_safe_member.member_name))
        if resp.status_code == HTTPStatus.OK:
            try:
                safe_member = ArkPCloudSafeMember.model_validate(resp.json())
                safe_member.permission_set = (
                    [p for p in SAFE_MEMBER_PERMISSIONS_SETS.keys() if SAFE_MEMBER_PERMISSIONS_SETS[p] == safe_member.permissions]
                    + [ArkPCloudSafeMemberPermissionSet.Custom]
                )[0]
                return safe_member
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse safe member response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse safe member response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve safe member [{resp.text}] - [{resp.status_code}]')

    def add_safe(self, add_safe: ArkPCloudAddSafe) -> ArkPCloudSafe:
        """
        Adds a new safe with given details
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Add%20Safe.htm

        Args:
            add_safe (ArkPCloudAddSafe): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafe: _description_
        """
        self._logger.info('Adding new safe')
        resp: Response = self._client.post(SAFES_URL, json=add_safe.model_dump(by_alias=True))
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkPCloudSafe.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add safe response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add safe response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add safe [{resp.text}] - [{resp.status_code}]')

    def add_safe_member(self, add_safe_member: ArkPCloudAddSafeMember) -> ArkPCloudSafeMember:
        """
        Adds a new member to a safe by given safe id and member name, along with fitting permissions or permission set
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Add%20Safe%20Member.htm

        Args:
            add_safe_member (ArkPCloudAddSafeMember): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafeMember: _description_
        """
        self._logger.info(f'Adding new safe member for safe [{add_safe_member.safe_id}] and name [{add_safe_member.member_name}]')
        if (
            add_safe_member.permission_set
            and add_safe_member.permission_set == ArkPCloudSafeMemberPermissionSet.Custom
            and not add_safe_member.permissions
        ):
            raise ArkServiceException('Custom permissions must have permissions model set')
        if add_safe_member.permission_set and add_safe_member.permission_set != ArkPCloudSafeMemberPermissionSet.Custom:
            add_safe_member.permissions = SAFE_MEMBER_PERMISSIONS_SETS[add_safe_member.permission_set].model_copy()
        resp: Response = self._client.post(
            SAFE_MEMBERS_URL.format(safe_id=add_safe_member.safe_id),
            json=add_safe_member.model_dump(by_alias=True, exclude={'safe_id', 'permission_set'}),
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkPCloudSafeMember.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add safe member response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add safe member response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add safe member [{resp.text}] - [{resp.status_code}]')

    def delete_safe(self, delete_safe: ArkPCloudDeleteSafe) -> None:
        """
        Deletes a safe by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Delete%20Safe.htm

        Args:
            delete_safe (ArkPCloudDeleteSafe): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting safe [{delete_safe.safe_id}]')
        resp: Response = self._client.delete(SAFE_URL.format(safe_id=delete_safe.safe_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete safe [{resp.text}] - [{resp.status_code}]')

    def delete_safe_member(self, delete_safe_member: ArkPCloudDeleteSafeMember) -> None:
        """
        Deletes a safe member from a safe by safe id and name
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Delete%20Safe%20Member.htm

        Args:
            delete_safe_member (ArkPCloudDeleteSafeMember): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting safe member from safe [{delete_safe_member.safe_id}] with name [{delete_safe_member.member_name}]')
        resp: Response = self._client.delete(
            f'{SAFE_MEMBER_URL.format(safe_id=delete_safe_member.safe_id, member_name=delete_safe_member.member_name)}/'
        )
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete safe member [{resp.text}] - [{resp.status_code}]')

    def update_safe(self, update_safe: ArkPCloudUpdateSafe) -> ArkPCloudSafe:
        """
        Updates safe details by safe id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Update%20Safe.htm

        Args:
            update_safe (ArkPCloudUpdateSafe): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafe: _description_
        """
        self._logger.info(f'Updating safe [{update_safe.safe_id}]')
        resp: Response = self._client.put(
            SAFE_URL.format(safe_id=update_safe.safe_id), json=update_safe.model_dump(by_alias=True, exclude={'safe_id'}, exclude_none=True)
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudSafe.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update safe response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update safe response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update safe [{resp.text}] - [{resp.status_code}]')

    def update_safe_member(self, update_safe_member: ArkPCloudUpdateSafeMember) -> ArkPCloudSafeMember:
        """
        Updates a safe member by safe id and member name
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Update%20Safe%20Member.htm

        Args:
            update_safe_member (ArkPCloudUpdateSafeMember): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudSafeMember: _description_
        """
        self._logger.info(f'Updating safe member of safe [{update_safe_member.safe_id}] and name [{update_safe_member.member_name}]')
        if (
            update_safe_member.permission_set
            and update_safe_member.permission_set == ArkPCloudSafeMemberPermissionSet.Custom
            and not update_safe_member.permissions
        ):
            raise ArkServiceException('Custom permissions must have permissions model set')
        if update_safe_member.permission_set and update_safe_member.permission_set != ArkPCloudSafeMemberPermissionSet.Custom:
            update_safe_member.permissions = SAFE_MEMBER_PERMISSIONS_SETS[update_safe_member.permission_set].model_copy()
        resp: Response = self._client.put(
            SAFE_MEMBER_URL.format(safe_id=update_safe_member.safe_id, member_name=update_safe_member.member_name),
            json=update_safe_member.model_dump(by_alias=True, exclude={'safe_id', 'member_name', 'permission_set'}, exclude_none=True),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudSafeMember.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update safe member response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update safe member response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update safe member [{resp.text}] - [{resp.status_code}]')

    def safes_stats(self) -> ArkPCloudSafesStats:
        """
        Calculates safe stats

        Returns:
            ArkPCloudSafesStats: _description_
        """
        self._logger.info('Calculating safes statistics')
        safes = list(itertools.chain.from_iterable([p.items for p in list(self.list_safes())]))
        safes_stats = ArkPCloudSafesStats.model_construct()
        safes_stats.safes_count = len(safes)

        # Get safes per location
        locations: Set[str] = {s.location for s in safes}
        safes_stats.safes_count_by_location = {l: len([s for s in safes if s.location == l]) for l in locations}

        # Get safes per creator
        creators: Set[str] = {s.creator.name for s in safes}
        safes_stats.safes_count_by_creator = {c: len([s for s in safes if s.creator.name == c]) for c in creators}

        return safes_stats

    def safe_members_stats(self, get_safe_members_stats: ArkPCloudGetSafeMembersStats) -> ArkPCloudSafeMembersStats:
        """
        Calculates safe members stats for a given safe

        Args:
            get_safe_members_stats (ArkPCloudGetSafeMembersStats): _description_

        Returns:
            ArkPCloudSafeMembersStats: _description_
        """
        self._logger.info(f'Calculating safe members statistics for safe [{get_safe_members_stats.safe_id}]')
        safe_members = list(
            itertools.chain.from_iterable(
                [p.items for p in list(self.list_safe_members(ArkPCloudListSafeMembers(safe_id=get_safe_members_stats.safe_id)))]
            )
        )
        safe_members_stats = ArkPCloudSafeMembersStats.model_construct()
        safe_members_stats.safe_members_count = len(safe_members)

        # Get safe members count and names per permission set
        permission_sets: Set[ArkPCloudSafeMemberPermissionSet] = {sm.permission_set for sm in safe_members}
        safe_members_stats.safe_members_permission_sets = {
            ps: ArkCountedValues(
                count=len([sm for sm in safe_members if sm.permission_set == ps]),
                values=[sm.member_name for sm in safe_members if sm.permission_set == ps],
            )
            for ps in permission_sets
        }

        # Get safe members count per type
        member_types: Set[ArkPCloudSafeMemberType] = {sm.member_type for sm in safe_members}
        safe_members_stats.safe_members_types_count = {mt: len([sm for sm in safe_members if sm.member_type == mt]) for mt in member_types}

        return safe_members_stats

    def safes_members_stats(self) -> ArkPCloudSafesMembersStats:
        """
        Calculates all safes members stats

        Returns:
            ArkPCloudSafesMembersStats: _description_
        """
        self._logger.info('Calculating safes members statistics')
        safes = list(itertools.chain.from_iterable([p.items for p in list(self.list_safes())]))
        safes_members_stats = ArkPCloudSafesMembersStats.model_construct()
        with ThreadPoolExecutor() as executor:
            safe_members_stats_tuples = executor.map(
                lambda s: (s.safe_name, self.safe_members_stats(ArkPCloudGetSafeMembersStats(safe_id=s.safe_id))), safes
            )
            safes_members_stats.safe_members_stats = dict((a, b) for a, b in safe_members_stats_tuples)
        return safes_members_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
