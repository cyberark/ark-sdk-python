from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Optional, Set

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.workspaces.db import (
    DATABASE_FAMILIES_DEFAULT_PORTS,
    DATABASES_ENGINES_TO_FAMILY,
    ArkDPADBAddDatabase,
    ArkDPADBDatabase,
    ArkDPADBDatabaseEngineType,
    ArkDPADBDatabaseFamilyType,
    ArkDPADBDatabaseInfoList,
    ArkDPADBDatabasesFilter,
    ArkDPADBDatabasesStats,
    ArkDPADBDatabaseWorkspaceType,
    ArkDPADBDeleteDatabase,
    ArkDPADBGetDatabase,
    ArkDPADBTag,
    ArkDPADBUpdateDatabase,
    ArkDPADBWarning,
    serialize_db_platform_type,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-workspaces-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
RESOURCES_API: Final[str] = 'api/adb/resources'
RESOURCE_API: Final[str] = 'api/adb/resources/{resource_id}'


class ArkDPADBWorkspaceService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    def __list_databases_with_filters(
        self, provider_family: Optional[ArkDPADBDatabaseFamilyType] = None, tags: Optional[List[ArkDPADBTag]] = None
    ) -> ArkDPADBDatabaseInfoList:
        params = {}
        if provider_family:
            params['provider-family'] = provider_family.value
        if tags:
            for tag in tags:
                params[f'key.{tag.key}'] = tag.value
        resp: Response = self.__client.get(RESOURCES_API, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBDatabaseInfoList.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list databases response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list databases response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list databases [{resp.text}] - [{resp.status_code}]')

    def add_database(self, add_database: ArkDPADBAddDatabase) -> ArkDPADBDatabase:
        """
        Adds a new database.

        Args:
            add_database (ArkDPADBAddDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBDatabase: _description_
        """
        self._logger.info(f'Adding database [{add_database.name}]')
        if not add_database.port:
            add_database.port = DATABASE_FAMILIES_DEFAULT_PORTS[DATABASES_ENGINES_TO_FAMILY[add_database.provider_engine]]
        add_database_dict = add_database.dict(exclude_none=True)
        add_database_dict['platform'] = serialize_db_platform_type(add_database.platform)
        resp: Response = self.__client.post(RESOURCES_API, json=add_database_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                database_id = resp.json()['target_id']
                return self.database(ArkDPADBGetDatabase(id=database_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add database [{resp.text}] - [{resp.status_code}]')

    def delete_database(self, delete_database: ArkDPADBDeleteDatabase) -> None:
        """
        Deletes a database.

        Args:
            delete_database (ArkDPADBDeleteDatabase): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_database.name and not delete_database.id:
            delete_database.id = self.list_databases_by(ArkDPADBDatabasesFilter(name=delete_database.name))
        self._logger.info(f'Deleting database [{delete_database.id}]')
        resp: Response = self.__client.delete(RESOURCE_API.format(resource_id=delete_database.id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete database [{resp.text}] - [{resp.status_code}]')

    def update_database(self, update_database: ArkDPADBUpdateDatabase) -> ArkDPADBDatabase:
        """
        Updates a database.

        Args:
            update_database (ArkDPADBUpdateDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBDatabase: _description_
        """
        if update_database.name and not update_database.id:
            update_database.id = self.list_databases_by(ArkDPADBDatabasesFilter(name=update_database.name))
        self._logger.info(f'Updating database [{update_database.id}]')
        update_database_dict = update_database.dict(exclude={'name', 'new_name'}, exclude_none=True)
        if update_database.new_name:
            update_database_dict["name"] = update_database.new_name
        resp: Response = self.__client.put(RESOURCE_API.format(resource_id=update_database.id), json=update_database_dict)
        if resp.status_code == HTTPStatus.OK:
            try:
                return self.database(ArkDPADBGetDatabase(id=update_database.id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update database [{resp.text}] - [{resp.status_code}]')

    def list_databases(self) -> ArkDPADBDatabaseInfoList:
        """
        Lists all databases.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBDatabaseInfoList: _description_
        """
        self._logger.info('Listing all databases')
        return self.__list_databases_with_filters()

    def list_databases_by(self, databases_filter: ArkDPADBDatabasesFilter) -> ArkDPADBDatabaseInfoList:
        """
        Lists databases that match the specified filters.

        Args:
            databases_filter (ArkDPADBDatabasesFilter): _description_

        Returns:
            ArkDPADBDatabaseInfoList: _description_
        """
        self._logger.info(f'Listing databases by filters [{databases_filter}]')
        databases = self.__list_databases_with_filters(databases_filter.provider_family, databases_filter.tags)
        if databases_filter.name:
            databases.items = [d for d in databases.items if fnmatch(d.name, databases_filter.name)]
        if databases_filter.provider_engine:
            databases.items = [d for d in databases.items if d.provider_info.engine == databases_filter.provider_engine]
        if databases_filter.provider_workspace:
            databases.items = [d for d in databases.items if d.provider_info.workspace == databases_filter.provider_workspace]
        if databases_filter.db_warnings_filter:
            if databases_filter.db_warnings_filter in (
                ArkDPADBWarning.AnyError,
                ArkDPADBWarning.NoCertificates,
            ):
                databases.items = [d for d in databases.items if not d.certificate]
            if databases_filter.db_warnings_filter in (
                ArkDPADBWarning.AnyError,
                ArkDPADBWarning.NoSecrets,
            ):
                databases.items = [d for d in databases.items if not d.secret_id]
        databases.total_count = len(databases.items)
        return databases

    def database(self, get_database: ArkDPADBGetDatabase) -> ArkDPADBDatabase:
        """
        Gets a specific database.

        Args:
            get_database (ArkDPADBGetDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBDatabase: _description_
        """
        if get_database.name and not get_database.id:
            get_database.id = self.list_databases_by(ArkDPADBDatabasesFilter(name=get_database.name))
        self._logger.info(f'Getting database [{get_database.id}]')
        resp: Response = self.__client.get(RESOURCE_API.format(resource_id=get_database.id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBDatabase.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to get database [{resp.text}] - [{resp.status_code}]')

    def databases_stats(self) -> ArkDPADBDatabasesStats:
        """
        Calculate statistics about the tenant's databases.

        Returns:
            ArkDPADBDatabasesStats: _description_
        """
        self._logger.info('Calculating databases stats')
        databases = self.list_databases()
        databases_stats = ArkDPADBDatabasesStats.construct()
        databases_stats.databases_count = len(databases.items)

        # Get databases per engine
        engines_types: Set[ArkDPADBDatabaseEngineType] = {d.provider_info.engine for d in databases.items}
        databases_stats.databases_count_by_engine = {
            et: len([d for d in databases.items if d.provider_info.engine == et]) for et in engines_types
        }

        # Get databases per workspace
        workspaces_types: Set[ArkDPADBDatabaseWorkspaceType] = {d.provider_info.workspace for d in databases.items}
        databases_stats.databases_count_by_workspace = {
            wt: len([d for d in databases.items if d.provider_info.workspace == wt]) for wt in workspaces_types
        }

        # Get databases per family
        family_types: Set[ArkDPADBDatabaseFamilyType] = {d.provider_info.family for d in databases.items}
        databases_stats.databases_count_by_family = {
            ft: len([d for d in databases.items if d.provider_info.family == ft]) for ft in family_types
        }

        # Get databases per db warning
        databases_stats.databases_count_by_warning = {
            ArkDPADBWarning.NoCertificates: len([d for d in databases.items if not d.certificate]),
            ArkDPADBWarning.NoSecrets: len([d for d in databases.items if not d.secret_id]),
        }

        return databases_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
