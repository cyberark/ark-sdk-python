import itertools
from http import HTTPStatus
from typing import Any, Final, Iterator, List, Optional, Type

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.cmgr import (
    ArkCmgrAddNetwork,
    ArkCmgrAddPool,
    ArkCmgrAddPoolBulkIdentifier,
    ArkCmgrAddPoolSingleIdentifier,
    ArkCmgrDeleteNetwork,
    ArkCmgrDeletePool,
    ArkCmgrDeletePoolBulkIdentifier,
    ArkCmgrDeletePoolSingleIdentifier,
    ArkCmgrGetNetwork,
    ArkCmgrGetPool,
    ArkCmgrGetPoolComponent,
    ArkCmgrListPoolIdentifiers,
    ArkCmgrNetwork,
    ArkCmgrNetworksFilter,
    ArkCmgrNetworksStats,
    ArkCmgrPool,
    ArkCmgrPoolComponent,
    ArkCmgrPoolComponentsFilter,
    ArkCmgrPoolIdentifier,
    ArkCmgrPoolIdentifiers,
    ArkCmgrPoolIdentifiersFilter,
    ArkCmgrPoolsCommonFilter,
    ArkCmgrPoolsFilter,
    ArkCmgrPoolsStats,
    ArkCmgrUpdateNetwork,
    ArkCmgrUpdatePool,
)
from ark_sdk_python.models.services.cmgr.ark_cmgr_bulk_response import ArkCmgrBulkResponses
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='cmgr', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
NETWORKS_API: Final[str] = 'api/pool-service/networks'
NETWORK_API: Final[str] = 'api/pool-service/networks/{network_id}'
POOLS_API: Final[str] = 'api/pool-service/pools'
POOL_API: Final[str] = 'api/pool-service/pools/{pool_id}'
POOL_IDENTIFIERS_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers'
POOL_IDENTIFIERS_BULK_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers-bulk'
POOL_IDENTIFIER_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers/{identifier_id}'
POOLS_COMPONENTS_API: Final[str] = 'api/pool-service/pools/components'
POOL_COMPONENT_API: Final[str] = 'api/pool-service/pools/{pool_id}/components/{component_id}'

ArkCmgrNetworkPage = ArkPage[ArkCmgrNetwork]
ArkCmgrPoolPage = ArkPage[ArkCmgrPool]
ArmCmgrPoolIdentifierPage = ArkPage[ArkCmgrPoolIdentifier]
ArkCmgrPoolComponentPage = ArkPage[ArkCmgrPoolComponent]


class ArkCmgrService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='connectormanagement',
            refresh_connection_callback=self.__refresh_cmgr_auth,
        )

    def __refresh_cmgr_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def __list_common_pools(
        self, name: str, route: str, item_type: Type[Any], common_filter: Optional[ArkCmgrPoolsCommonFilter] = None
    ) -> Iterator[Any]:
        cont_token = None
        filters = {'projection': 'EXTENDED'}
        if common_filter:
            filters.update(common_filter.model_dump(exclude_none=True))
        while True:
            resp = self.__client.get(route, params=filters)
            if resp.status_code != HTTPStatus.OK:
                raise ArkServiceException(f'Failed to list {name} [{resp.text}] - [{resp.status_code}]')
            result = resp.json()
            yield ArkPage[item_type](TypeAdapter(List[item_type]).validate_python(result['resources']))
            if 'page' not in result:
                break
            page = result['page']
            if 'continuation_token' not in page or not page['continuation_token']:
                break
            cont_token = page['continuation_token']
            if 'total_resources_count' in page and page['total_resources_count'] and page['page_size'] == page['total_resources_count']:
                break
            filters['continuation_token'] = cont_token

    @staticmethod
    def __identifiers_by_add_pool_identifies_response(response: Response) -> ArkCmgrPoolIdentifiers:
        identifiers_responses: ArkCmgrBulkResponses = ArkCmgrBulkResponses.model_validate(response.json())
        identifiers: List[ArkCmgrPoolIdentifier] = []
        for identifier_response in identifiers_responses.responses.values():
            if identifier_response.status_code != HTTPStatus.CREATED:
                raise ArkServiceException(f'Failed to add pool identifiers bulk [{response.text}] - [{response.status_code}]')
            identifiers.append(ArkCmgrPoolIdentifier.model_validate(identifier_response.body))

        return ArkCmgrPoolIdentifiers(identifiers=identifiers)

    def add_network(self, add_network: ArkCmgrAddNetwork) -> ArkCmgrNetwork:
        """
        Adds a new network

        Args:
            add_network (ArkCmgrAddNetwork): _description_

        Returns:
            ArkCmgrNetwork: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding new network [{add_network}]')
        resp: Response = self.__client.post(NETWORKS_API, json=add_network.model_dump())
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkCmgrNetwork.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add network response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add network response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add network [{resp.text}] - [{resp.status_code}]')

    def update_network(self, update_network: ArkCmgrUpdateNetwork) -> ArkCmgrNetwork:
        """
        Updates a network

        Args:
            update_network (ArkCmgrUpdateNetwork): _description_

        Returns:
            ArkCmgrNetwork: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Updating network [{update_network}]')
        if not update_network.name:
            self._logger.info('Nothing to update')
            return self.network(ArkCmgrGetNetwork(network_id=update_network.network_id))
        resp: Response = self.__client.patch(
            NETWORK_API.format(network_id=update_network.network_id), json=update_network.model_dump(exclude={'network_id'})
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrNetwork.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update network response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update network response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update network [{resp.text}] - [{resp.status_code}]')

    def delete_network(self, delete_network: ArkCmgrDeleteNetwork) -> None:
        """
        Deletes the given network.

        Args:
            delete_network (ArkCmgrDeleteNetwork): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting network [{delete_network}]')
        resp: Response = self.__client.delete(NETWORK_API.format(network_id=delete_network.network_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete network [{resp.text}] - [{resp.status_code}]')

    def list_networks(self) -> Iterator[ArkCmgrNetworkPage]:
        """
        Listing all networks, yielding in pages

        Yields:
            Iterator[ArkCmgrNetworkPage]: _description_
        """
        self._logger.info('Listing all networks')
        yield from self.__list_common_pools(
            'networks',
            NETWORKS_API,
            ArkCmgrNetwork,
        )

    def list_networks_by(self, networks_filter: ArkCmgrNetworksFilter) -> Iterator[ArkCmgrNetworkPage]:
        """
        Listing networks by filters, yielding in pages

        Args:
            networks_filter (ArkCmgrNetworksFilter): _description_

        Yields:
            Iterator[ArkCmgrNetworkPage]: _description_
        """
        self._logger.info(f'Listing networks by filters [{networks_filter}]')
        yield from self.__list_common_pools(
            'networks',
            NETWORKS_API,
            ArkCmgrNetwork,
            networks_filter,
        )

    def network(self, get_network: ArkCmgrGetNetwork) -> ArkCmgrNetwork:
        """
        Retrieves a network by ID.

        Args:
            get_network (ArkCmgrGetNetwork): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrNetwork: _description_
        """
        self._logger.info(f'Retrieving network [{get_network}]')
        resp: Response = self.__client.get(NETWORK_API.format(network_id=get_network.network_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrNetwork.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse network response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse network response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve network [{get_network.network_id}] [{resp.text}] - [{resp.status_code}]')

    def networks_stats(self) -> ArkCmgrNetworksStats:
        """
        Calculates network statistics.

        Returns:
            ArkCmgrNetworksStats: _description_
        """
        self._logger.info('Calculating network stats')
        networks = list(itertools.chain.from_iterable([p.items for p in list(self.list_networks())]))
        networks_stats = ArkCmgrNetworksStats.model_construct()
        networks_stats.networks_count = len(networks)
        networks_stats.pools_count_per_network = {n.name: len(n.assigned_pools) for n in networks}
        return networks_stats

    def add_pool(self, add_pool: ArkCmgrAddPool) -> ArkCmgrPool:
        """
        Adds a new pool

        Args:
            add_pool (ArkCmgrAddPool): _description_

        Returns:
            ArkCmgrPool: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding new pool [{add_pool}]')
        resp: Response = self.__client.post(POOLS_API, json=add_pool.model_dump())
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkCmgrPool.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add pool response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add pool response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add pool [{resp.text}] - [{resp.status_code}]')

    def update_pool(self, update_pool: ArkCmgrUpdatePool) -> ArkCmgrPool:
        """
        Updates a pool

        Args:
            update_pool (ArkCmgrUpdatePool): _description_

        Returns:
            ArkCmgrNetwork: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Updating pool [{update_pool}]')
        if not update_pool.name and not update_pool.assigned_network_ids and not update_pool.description:
            self._logger.info('Nothing to update')
            return self.pool(ArkCmgrGetPool(pool_id=update_pool.pool_id))
        resp: Response = self.__client.patch(POOL_API.format(pool_id=update_pool.pool_id), json=update_pool.model_dump(exclude={'pool_id'}))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrPool.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update pool response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update pool response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update pool [{resp.text}] - [{resp.status_code}]')

    def delete_pool(self, delete_pool: ArkCmgrDeletePool) -> None:
        """
        Deletes the given pool.

        Args:
            delete_pool (ArkCmgrDeletePool): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting pool [{delete_pool}]')
        resp: Response = self.__client.delete(POOL_API.format(pool_id=delete_pool.pool_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete pool [{resp.text}] - [{resp.status_code}]')

    def list_pools(self) -> Iterator[ArkCmgrPoolPage]:
        """
        Listing all pools, yielding in pages

        Yields:
            Iterator[ArkCmgrPoolPage]: _description_
        """
        self._logger.info('Listing all pools')
        yield from self.__list_common_pools(
            'pools',
            POOLS_API,
            ArkCmgrPool,
        )

    def list_pools_by(self, pools_filter: ArkCmgrPoolsFilter) -> Iterator[ArkCmgrPoolPage]:
        """
        Listing pools by filters, yielding in pages

        Args:
            pools_filter (ArkCmgrPoolsFilter): _description_

        Yields:
            Iterator[ArkCmgrNetworkPage]: _description_
        """
        self._logger.info(f'Listing pools by filters [{pools_filter}]')
        yield from self.__list_common_pools(
            'pools',
            POOLS_API,
            ArkCmgrPool,
            pools_filter,
        )

    def pool(self, get_pool: ArkCmgrGetPool) -> ArkCmgrPool:
        """
        Retrieves a pool by ID.

        Args:
            get_pool (ArkCmgrGetPool): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrPool: _description_
        """
        self._logger.info(f'Retrieving pool [{get_pool}]')
        resp: Response = self.__client.get(POOL_API.format(pool_id=get_pool.pool_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrPool.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse pool response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse pool response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve pool [{get_pool.pool_id}] [{resp.text}] - [{resp.status_code}]')

    def pools_stats(self) -> ArkCmgrPoolsStats:
        """
        Calculates pools statistics.

        Returns:
            ArkCmgrPoolsStats: _description_
        """
        self._logger.info('Calculating pools stats')
        pools = list(itertools.chain.from_iterable([p.items for p in list(self.list_pools())]))
        pools_stats = ArkCmgrPoolsStats.model_construct()
        pools_stats.pools_count = len(pools)
        pools_stats.networks_count_per_pool = {p.name: len(p.assigned_network_ids) for p in pools}
        pools_stats.identifiers_count_per_pool = {p.name: p.identifiers_count for p in pools}
        pools_stats.components_count_per_pool = {p.name: p.components_count for p in pools}
        return pools_stats

    def add_pool_identifier(self, add_identifier: ArkCmgrAddPoolSingleIdentifier) -> ArkCmgrPoolIdentifier:
        """
        Adds a new pool identifier

        Args:
            add_identifier (ArkCmgrAddPoolSingleIdentifier): _description_

        Returns:
            ArkCmgrPoolIdentifier: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Adding new pool identifier [{add_identifier}]')
        resp: Response = self.__client.post(
            POOL_IDENTIFIERS_API.format(pool_id=add_identifier.pool_id), json=add_identifier.model_dump(exclude={'pool_id'})
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkCmgrPoolIdentifier.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add pool identifier response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add pool identifier response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add pool identifier [{resp.text}] - [{resp.status_code}]')

    def add_pool_identifiers(self, add_identifiers: ArkCmgrAddPoolBulkIdentifier) -> ArkCmgrPoolIdentifiers:
        """
        Adds a bulk of new pool identifiers.

        Args:
            add_identifiers (ArkCmgrAddPoolBulkIdentifier): The identifiers to add.

        Returns:
            ArkCmgrPoolIdentifiers: Detailed information about the added identifiers.

        Raises:
            ArkServiceException: In case the response is not MULTI_STATUS, or if one of the responses is not CREATED.
        """
        self._logger.info(f'Adding new pool identifiers bulk [{add_identifiers}]')
        response: Response = self.__client.post(
            POOL_IDENTIFIERS_BULK_API.format(pool_id=add_identifiers.pool_id),
            json={
                'requests': {str(index): i.model_dump(exclude={'pool_id'}) for index, i in enumerate(add_identifiers.identifiers, start=1)}
            },
        )
        if response.status_code == HTTPStatus.MULTI_STATUS:
            try:
                return self.__identifiers_by_add_pool_identifies_response(response=response)
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add pool identifiers bulk response [{str(ex)}] - [{response.text}]')
                raise ArkServiceException(f'Failed to parse add pool identifiers bulk response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add pool identifiers bulk [{response.text}] - [{response.status_code}]')

    def delete_pool_identifier(self, delete_identifier: ArkCmgrDeletePoolSingleIdentifier) -> None:
        """
        Deletes the given pool identifier

        Args:
            delete_identifier (ArkCmgrDeletePoolSingleIdentifier): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting pool identifier [{delete_identifier}]')
        resp: Response = self.__client.delete(
            POOL_IDENTIFIER_API.format(pool_id=delete_identifier.pool_id, identifier_id=delete_identifier.identifier_id)
        )
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete pool identifier [{resp.text}] - [{resp.status_code}]')

    def delete_pool_identifiers(self, delete_identifiers: ArkCmgrDeletePoolBulkIdentifier) -> None:
        """
        Deletes the given bulk of pool identifiers.

        Args:
            delete_identifiers (ArkCmgrDeletePoolBulkIdentifier): List of identifiers to delete.

        Raises:
            ArkServiceException: In case the response is not MULTI_STATUS, or if one of the responses is not NO_CONTENT.
        """
        self._logger.info(f'Deleting pool identifiers bulk [{delete_identifiers}]')
        resp: Response = self.__client.delete(
            POOL_IDENTIFIERS_BULK_API.format(pool_id=delete_identifiers.pool_id),
            json={'requests': {str(index): {'id': i.identifier_id} for index, i in enumerate(delete_identifiers.identifiers, start=1)}},
        )
        if resp.status_code == HTTPStatus.MULTI_STATUS:
            delete_responses: ArkCmgrBulkResponses = ArkCmgrBulkResponses.model_validate(resp.json())
            for _, identifier_response in delete_responses.responses.items():
                if identifier_response.status_code != HTTPStatus.NO_CONTENT:
                    raise ArkServiceException(f'Failed to delete pool identifiers [{resp.text}] - [{resp.status_code}]')
        else:
            raise ArkServiceException(f'Failed to delete pool identifier [{resp.text}] - [{resp.status_code}]')

    def list_pool_identifiers(self, list_identifiers: ArkCmgrListPoolIdentifiers) -> Iterator[ArmCmgrPoolIdentifierPage]:
        """
        Listing all pool identifiers, yielding in pages

        Args:
            list_identifiers (ArkCmgrListPoolIdentifiers): _description_

        Yields:
            Iterator[ArmCmgrPoolIdentifierPage]: _description_
        """
        self._logger.info(f'Listing all pool [{list_identifiers}] identifiers')
        yield from self.__list_common_pools(
            'pool identifiers',
            POOL_IDENTIFIERS_API.format(pool_id=list_identifiers.pool_id),
            ArkCmgrPoolIdentifier,
        )

    def list_pool_identifiers_by(self, identifiers_filter: ArkCmgrPoolIdentifiersFilter) -> Iterator[ArmCmgrPoolIdentifierPage]:
        """
        Listing pool identifiers with filters, yielding in pages

        Args:
            identifiers_filter (ArkCmgrPoolIdentifiersFilter): _description_

        Yields:
            Iterator[ArmCmgrPoolIdentifierPage]: _description_
        """
        self._logger.info(f'Listing pool identifiers with filters [{identifiers_filter}]')
        yield from self.__list_common_pools(
            'pool identifiers',
            POOL_IDENTIFIERS_API.format(pool_id=identifiers_filter.pool_id),
            ArkCmgrPoolIdentifier,
            ArkCmgrPoolsCommonFilter(**identifiers_filter.model_dump()),
        )

    def list_pools_components(self) -> Iterator[ArkCmgrPoolComponentPage]:
        """
        Listing all pools components, yielding in pages

        Yields:
            Iterator[ArkCmgrPoolComponentPage]: _description_
        """
        self._logger.info('Listing all pools components')
        yield from self.__list_common_pools(
            'pools components',
            POOLS_COMPONENTS_API,
            ArkCmgrPoolComponent,
        )

    def list_pools_components_by(self, components_filter: ArkCmgrPoolComponentsFilter) -> Iterator[ArkCmgrPoolComponentPage]:
        """
        Listing pools components with filters, yielding in pages

        Args:
            components_filter (ArkCmgrPoolComponentsFilter): _description_

        Yields:
            Iterator[ArkCmgrPoolComponentPage]: _description_
        """
        self._logger.info(f'Listing pool components with filters [{components_filter}]')
        yield from self.__list_common_pools(
            'pools components',
            POOLS_COMPONENTS_API,
            ArkCmgrPoolIdentifier,
            ArkCmgrPoolsCommonFilter(**components_filter.model_dump()),
        )

    def pool_component(self, get_pool_component: ArkCmgrGetPoolComponent) -> ArkCmgrPoolComponent:
        """
        Retrieves a pool component by ID.

        Args:
            get_pool_component (ArkCmgrGetPoolComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrPoolComponent: _description_
        """
        self._logger.info(f'Retrieving pool component [{get_pool_component}]')
        resp: Response = self.__client.get(
            POOL_COMPONENT_API.format(pool_id=get_pool_component.pool_id, component_id=get_pool_component.component_id)
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrPoolComponent.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse pool component response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse pool component  response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve pool component [{get_pool_component}] [{resp.text}] - [{resp.status_code}]')

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
