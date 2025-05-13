from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Optional, Set

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.workspaces.db import (
    DATABASE_FAMILIES_DEFAULT_PORTS,
    DATABASES_ENGINES_TO_FAMILY,
    ArkSIADBAddDatabase,
    ArkSIADBAuthMethodType,
    ArkSIADBDatabase,
    ArkSIADBDatabaseEngineType,
    ArkSIADBDatabaseFamilyType,
    ArkSIADBDatabaseInfoList,
    ArkSIADBDatabasesFilter,
    ArkSIADBDatabasesStats,
    ArkSIADBDatabaseWorkspaceType,
    ArkSIADBDeleteDatabase,
    ArkSIADBGetDatabase,
    ArkSIADBTag,
    ArkSIADBUpdateDatabase,
    ArkSIADBWarning,
    serialize_db_platform_type,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-workspaces-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
RESOURCES_API: Final[str] = 'api/adb/resources'
RESOURCE_API: Final[str] = 'api/adb/resources/{resource_id}'


class ArkSIADBWorkspaceService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='dpa',
            refresh_connection_callback=self.__refresh_sia_auth,
        )

    def __refresh_sia_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def __list_databases_with_filters(
        self, provider_family: Optional[ArkSIADBDatabaseFamilyType] = None, tags: Optional[List[ArkSIADBTag]] = None
    ) -> ArkSIADBDatabaseInfoList:
        params = {}
        if provider_family:
            params['provider-family'] = provider_family.value
        if tags:
            for tag in tags:
                params[f'key.{tag.key}'] = tag.value
        resp: Response = self.__client.get(RESOURCES_API, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBDatabaseInfoList.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list databases response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list databases response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list databases [{resp.text}] - [{resp.status_code}]')

    def add_database(self, add_database: ArkSIADBAddDatabase) -> ArkSIADBDatabase:
        """
        Adds a new database.

        Args:
            add_database (ArkSIADBAddDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBDatabase: _description_
        """
        self._logger.info(f'Adding database [{add_database.name}]')
        if not add_database.port:
            add_database.port = DATABASE_FAMILIES_DEFAULT_PORTS[DATABASES_ENGINES_TO_FAMILY[add_database.provider_engine]]
        add_database_dict = add_database.model_dump(exclude_none=True)
        add_database_dict['platform'] = serialize_db_platform_type(add_database.platform)
        resp: Response = self.__client.post(RESOURCES_API, json=add_database_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                database_id = resp.json()['target_id']
                return self.database(ArkSIADBGetDatabase(id=database_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add database [{resp.text}] - [{resp.status_code}]')

    def delete_database(self, delete_database: ArkSIADBDeleteDatabase) -> None:
        """
        Deletes a database.

        Args:
            delete_database (ArkSIADBDeleteDatabase): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_database.name and not delete_database.id:
            databases = self.list_databases_by(ArkSIADBDatabasesFilter(name=delete_database.name))
            if not databases.items or len(databases.items) != 1:
                raise ArkServiceException(f'Failed to delete database - name [{delete_database.name}] not found')
            delete_database.id = databases.items[0].id
        self._logger.info(f'Deleting database [{delete_database.id}]')
        resp: Response = self.__client.delete(RESOURCE_API.format(resource_id=delete_database.id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete database [{resp.text}] - [{resp.status_code}]')

    def update_database(self, update_database: ArkSIADBUpdateDatabase) -> ArkSIADBDatabase:
        """
        Updates a database.

        Args:
            update_database (ArkSIADBUpdateDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBDatabase: _description_
        """
        if update_database.name and not update_database.id:
            databases = self.list_databases_by(ArkSIADBDatabasesFilter(name=update_database.name))
            if not databases.items or len(databases.items) != 1:
                raise ArkServiceException(f'Failed to update database - name [{update_database.name}] not found')
            update_database.id = databases.items[0].id

        existing_database = self.database(ArkSIADBGetDatabase(id=update_database.id))
        self._logger.info(f'Updating database [{update_database.id}]')
        update_database_dict = update_database.model_dump(exclude={'name', 'new_name'}, exclude_none=True)
        if update_database.new_name:
            update_database_dict["name"] = update_database.new_name
        elif update_database.name:
            update_database_dict["name"] = update_database.name
        else:
            update_database_dict["name"] = existing_database.name
        resp: Response = self.__client.put(RESOURCE_API.format(resource_id=update_database.id), json=update_database_dict)
        if resp.status_code == HTTPStatus.OK:
            try:
                return self.database(ArkSIADBGetDatabase(id=update_database.id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update database [{resp.text}] - [{resp.status_code}]')

    def list_databases(self) -> ArkSIADBDatabaseInfoList:
        """
        Lists all databases.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBDatabaseInfoList: _description_
        """
        self._logger.info('Listing all databases')
        return self.__list_databases_with_filters()

    def list_databases_by(self, databases_filter: ArkSIADBDatabasesFilter) -> ArkSIADBDatabaseInfoList:
        """
        Lists databases that match the specified filters.

        Args:
            databases_filter (ArkSIADBDatabasesFilter): _description_

        Returns:
            ArkSIADBDatabaseInfoList: _description_
        """
        self._logger.info(f'Listing databases by filters [{databases_filter}]')
        databases = self.__list_databases_with_filters(databases_filter.provider_family, databases_filter.tags)
        if databases_filter.name:
            databases.items = [d for d in databases.items if fnmatch(d.name, databases_filter.name)]
        if databases_filter.provider_engine:
            databases.items = [d for d in databases.items if d.provider_info.engine == databases_filter.provider_engine]
        if databases_filter.provider_workspace:
            databases.items = [d for d in databases.items if d.provider_info.workspace == databases_filter.provider_workspace]
        if databases_filter.auth_methods:
            databases.items = [d for d in databases.items if d.configured_auth_method_type in databases_filter.auth_methods]
        if databases_filter.db_warnings_filter:
            if databases_filter.db_warnings_filter in (
                ArkSIADBWarning.AnyError,
                ArkSIADBWarning.NoCertificates,
            ):
                databases.items = [d for d in databases.items if not d.certificate]
            if databases_filter.db_warnings_filter in (
                ArkSIADBWarning.AnyError,
                ArkSIADBWarning.NoSecrets,
            ):
                databases.items = [d for d in databases.items if not d.secret_id]
        databases.total_count = len(databases.items)
        return databases

    def database(self, get_database: ArkSIADBGetDatabase) -> ArkSIADBDatabase:
        """
        Gets a specific database.

        Args:
            get_database (ArkSIADBGetDatabase): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBDatabase: _description_
        """
        if get_database.name and not get_database.id:
            databases = self.list_databases_by(ArkSIADBDatabasesFilter(name=get_database.name))
            if not databases.items or len(databases.items) != 1:
                raise ArkServiceException(f'Failed to get database - name [{get_database.name}] not found')
            get_database.id = databases.items[0].id
        self._logger.info(f'Getting database [{get_database.id}]')
        resp: Response = self.__client.get(RESOURCE_API.format(resource_id=get_database.id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBDatabase.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse database response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse database response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to get database [{resp.text}] - [{resp.status_code}]')

    def databases_stats(self) -> ArkSIADBDatabasesStats:
        """
        Calculate statistics about the tenant's databases.

        Returns:
            ArkSIADBDatabasesStats: _description_
        """
        self._logger.info('Calculating databases stats')
        databases = self.list_databases()
        databases_stats = ArkSIADBDatabasesStats.model_construct()
        databases_stats.databases_count = len(databases.items)

        # Get databases per engine
        engines_types: Set[ArkSIADBDatabaseEngineType] = {d.provider_info.engine for d in databases.items}
        databases_stats.databases_count_by_engine = {
            et: len([d for d in databases.items if d.provider_info.engine == et]) for et in engines_types
        }

        # Get databases per workspace
        workspaces_types: Set[ArkSIADBDatabaseWorkspaceType] = {d.provider_info.workspace for d in databases.items}
        databases_stats.databases_count_by_workspace = {
            wt: len([d for d in databases.items if d.provider_info.workspace == wt]) for wt in workspaces_types
        }

        # Get databases per family
        family_types: Set[ArkSIADBDatabaseFamilyType] = {d.provider_info.family for d in databases.items}
        databases_stats.databases_count_by_family = {
            ft: len([d for d in databases.items if d.provider_info.family == ft]) for ft in family_types
        }

        # Get databases per auth method
        auth_method_types: Set[ArkSIADBAuthMethodType] = {d.configured_auth_method_type for d in databases.items}
        databases_stats.databases_count_by_auth_method = {
            am: len([d for d in databases.items if d.configured_auth_method_type == am]) for am in auth_method_types
        }

        # Get databases per db warning
        databases_stats.databases_count_by_warning = {
            ArkSIADBWarning.NoCertificates: len([d for d in databases.items if not d.certificate]),
            ArkSIADBWarning.NoSecrets: len([d for d in databases.items if not d.secret_id]),
        }

        return databases_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
