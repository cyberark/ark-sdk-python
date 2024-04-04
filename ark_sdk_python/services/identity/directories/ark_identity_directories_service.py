from http import HTTPStatus
from typing import Final, Iterator, List

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.env import SHELL_DOMAIN, check_if_identity_generated_suffix
from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.common.identity import (
    DirectorySearchArgs,
    DirectoryService,
    DirectoryServiceQueryResponse,
    GetDirectoryServicesResponse,
    GetTenantSuffixResult,
)
from ark_sdk_python.models.common.identity.ark_identity_directory_schemas import DirectoryServiceQueryRequest
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.directories import (
    ArkIdentityDirectory,
    ArkIdentityEntity,
    ArkIdentityEntityType,
    ArkIdentityGroupEntity,
    ArkIdentityListDirectories,
    ArkIdentityListDirectoriesEntities,
    ArkIdentityRoleEntity,
    ArkIdentityUserEntity,
)
from ark_sdk_python.services.identity.common import ArkIdentityBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-directories', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

TENANT_SUFFIX_URL: Final[str] = 'Core/GetCdsAliasesForTenant'
GET_DIRECTORY_SERVICES_URL: Final[str] = 'Core/GetDirectoryServices'
DIRECTORY_SERVICE_QUERY_URL: Final[str] = 'UserMgmt/DirectoryServiceQuery'

ArkIdentityEntitiesPage = ArkPage[ArkIdentityEntity]


class ArkIdentityDirectoriesService(ArkIdentityBaseService):
    def list_directories(self, list_directories: ArkIdentityListDirectories) -> List[ArkIdentityDirectory]:
        """
        Get directories for given types

        Args:
            list_directories (ArkIdentityListDirectories): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkIdentityDirectory]: _description_
        """
        if not list_directories.directories:
            list_directories.directories = [d for d in DirectoryService]
        self._logger.info(f'Retrieving directory services for directories [{list_directories}] [{self._url_prefix}]')
        response: Response = self._client.get(f'{self._url_prefix}{GET_DIRECTORY_SERVICES_URL}', data={})
        try:
            directory_services_result = GetDirectoryServicesResponse.parse_raw(response.text)
            requested_directories = set(item.value for item in list_directories.directories)
            requested_services = list(
                filter(lambda service: service.row.service in requested_directories, directory_services_result.result.results)
            )
            if len(requested_services) == 0:
                raise ArkServiceException(f'Could not find any directory services matching {requested_directories}')
            directories = list(
                map(
                    lambda service: ArkIdentityDirectory(
                        directory=DirectoryService(service.row.service), directory_service_uuid=service.row.directory_service_uuid
                    ),
                    requested_services,
                )
            )
            return directories
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to parse directory services response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse directory services response [{str(ex)}]') from ex

    def list_directories_entities(self, list_directories_entities: ArkIdentityListDirectoriesEntities) -> Iterator[ArkIdentityEntitiesPage]:
        """
        Lists given directories entities by filters of search and type and directories
        Yields pages of entities

        Args:
            list_directories_entities (ArkIdentityListDirectoriesEntities): _description_

        Raises:
            ArkServiceException: _description_

        Yields:
            Iterator[ArkIdentityEntitiesPage]: _description_
        """
        self._logger.info('Listing directories entities')
        directories = [
            d.directory_service_uuid
            for d in self.list_directories(
                ArkIdentityListDirectories(directories=list_directories_entities.directories or [d for d in DirectoryService])
            )
        ]
        exclusion_list = set()
        if list_directories_entities.entity_types:
            if ArkIdentityEntityType.User not in list_directories_entities.entity_types:
                exclusion_list.add('user')
            if ArkIdentityEntityType.Group not in list_directories_entities.entity_types:
                exclusion_list.add('group')
            if ArkIdentityEntityType.Role not in list_directories_entities.entity_types:
                exclusion_list.add('roles')
        response: Response = self._idp_client.post(
            DIRECTORY_SERVICE_QUERY_URL,
            data=DirectoryServiceQueryRequest(
                directory_services=directories,
                search_string=list_directories_entities.search,
                args=DirectorySearchArgs(
                    limit=list_directories_entities.limit, page_number=1, page_size=list_directories_entities.page_size
                ),
            ).json(by_alias=True, exclude=exclusion_list),
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to query for directory services entities [{response.text}] - [{response.status_code}]')
        try:
            result = DirectoryServiceQueryResponse.parse_raw(response.text)
            entities: List[ArkIdentityEntity] = []
            if result.result.users and result.result.users.results:
                for user in result.result.users.results:
                    entities.append(
                        ArkIdentityUserEntity(
                            id=user.row.internal_id,
                            name=user.row.system_name,
                            entity_type=ArkIdentityEntityType.User,
                            directory_service_type=user.row.directory_service_type,
                            display_name=user.row.display_name,
                            service_instance_localized=user.row.service_instance_localized,
                            email=user.row.email,
                            description=user.row.description,
                        )
                    )
            if result.result.groups and result.result.groups.results:
                for group in result.result.groups.results:
                    entities.append(
                        ArkIdentityGroupEntity(
                            id=group.row.internal_id,
                            name=group.row.system_name,
                            entity_type=ArkIdentityEntityType.Group,
                            directory_service_type=group.row.directory_service_type,
                            display_name=group.row.display_name,
                            service_instance_localized=group.row.service_instance_localized,
                        )
                    )
            if result.result.roles and result.result.roles.results:
                for role in result.result.roles.results:
                    entities.append(
                        ArkIdentityRoleEntity(
                            id=role.row.id,
                            name=role.row.name,
                            entity_type=ArkIdentityEntityType.Role,
                            directory_service_type=DirectoryService.Identity,
                            display_name=role.row.name,
                            service_instance_localized=DirectoryService.Identity.value,
                            admin_rights=role.row.admin_rights,
                            is_hidden=role.row.is_hidden or False,
                            description=role.row.description,
                        )
                    )
            while entities:
                if len(entities) <= list_directories_entities.page_size:
                    yield ArkIdentityEntitiesPage(entities)
                    break
                else:
                    page = entities[: list_directories_entities.page_size]
                    entities = entities[list_directories_entities.page_size :]
                    yield ArkIdentityEntitiesPage(page)
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to parse list directories entities response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse list directories entities response [{str(ex)}]') from ex

    def tenant_default_suffix(self) -> str:
        """
        Retrieves the tenant default suffix found in identity
        The suffix is used when creating users based on whats configured on the tenant

        Raises:
            ArkServiceException: _description_

        Returns:
            str: _description_
        """
        self._logger.info('Discovering default tenant suffix')
        response: Response = self._client.post(f'{self._url_prefix}{TENANT_SUFFIX_URL}')
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get directory services [{response.text}]')
        try:
            tenant_suffixes_result: GetTenantSuffixResult = GetTenantSuffixResult.parse_raw(response.text)
            tenant_suffixes_list: List[str] = [result['Entities'][0]['Key'] for result in tenant_suffixes_result.result['Results']]
            if len(tenant_suffixes_list) == 0:
                raise ArkServiceException('No tenant suffix has been found')
            filtered_urls = list(
                filter(
                    lambda suffix: check_if_identity_generated_suffix(suffix, self._env) or SHELL_DOMAIN[self._env] in suffix,
                    tenant_suffixes_list,
                )
            )
            if filtered_urls:
                return filtered_urls[0]
            return tenant_suffixes_list[0]
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse tenant default suffix response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse tenant default suffix response [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
