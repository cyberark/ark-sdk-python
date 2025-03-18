from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.connectors import (
    ArkIdentityConnectorInfo,
    ArkIdentityConnectorsFilter,
    ArkIdentityGetConnector,
)
from ark_sdk_python.services.identity.common import ArkIdentityBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-connectors', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

REDROCK_QUERY: Final[str] = 'Redrock/query'


class ArkIdentityConnectorsService(ArkIdentityBaseService):
    def list_connectors(self) -> List[ArkIdentityConnectorInfo]:
        """
        Lists all identity connectors on the tenant

        Returns:
            List[ArkIdentityConnectorInfo]: _description_
        """
        self._logger.info('Listing all identity connectors')
        response: Response = self._client.post(
            f'{self._url_prefix}{REDROCK_QUERY}',
            json={"Script": "Select * from Proxy"},
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to retrieve identity connectors [{response.text}] - [{response.status_code}]')
        try:
            query_result = response.json()
            if not query_result['success']:
                raise ArkServiceException('Failed to retrieve identity connectors')
            if len(query_result['Result']["Results"]) == 0:
                return []
            return TypeAdapter(List[ArkIdentityConnectorInfo]).validate_python([r['Row'] for r in query_result['Result']["Results"]])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to retrieve identity connectors [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to retrieve identity connectors [{str(ex)}]') from ex

    def list_connectors_by(self, connectors_filter: ArkIdentityConnectorsFilter) -> List[ArkIdentityConnectorInfo]:
        """
        Lists identity connectors on the tenant by filters

        Args:
            connectors_filter (ArkIdentityConnectorsFilter): _description_

        Returns:
            List[ArkIdentityConnectorInfo]: _description_
        """
        self._logger.info(f'Listing identity connectors by filters [{connectors_filter}]')
        connectors = self.list_connectors()

        # Filter by connector online / offline
        if connectors_filter.online is not None:
            connectors = [c for c in connectors if c.online == connectors_filter.online]

        # Filter by forest
        if connectors_filter.forest:
            connectors = [c for c in connectors if fnmatch(c.forest, connectors_filter.forest)]

        # Filter by dns
        if connectors_filter.dns:
            connectors = [c for c in connectors if fnmatch(c.dns_host_name, connectors_filter.dns)]

        # Filter by machine name
        if connectors_filter.machine_name:
            connectors = [c for c in connectors if fnmatch(c.machine_name, connectors_filter.machine_name)]

        # Filter by customer name
        if connectors_filter.customer_name:
            connectors = [c for c in connectors if fnmatch(c.customer_name, connectors_filter.customer_name)]

        # Filter by forest
        if connectors_filter.version:
            connectors = [c for c in connectors if fnmatch(c.version, connectors_filter.version)]

        return connectors

    def connector(self, get_connector: ArkIdentityGetConnector) -> ArkIdentityConnectorInfo:
        """
        Retrieves a connector by id

        Args:
            get_connector (ArkIdentityGetConnector): _description_

        Returns:
            ArkIdentityConnectorInfo: _description_
        """
        self._logger.info(f'Retrieving identity connector by id [{get_connector.connector_id}]')
        response: Response = self._client.post(
            f'{self._url_prefix}{REDROCK_QUERY}',
            json={"Script": f"Select * from Proxy WHERE ID='{get_connector.connector_id}'"},
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to retrieve identity connector by id [{response.text}] - [{response.status_code}]')
        try:
            query_result = response.json()
            if not query_result['success'] or len(query_result['Result']["Results"]) == 0:
                raise ArkServiceException('Failed to retrieve identity connector by id')
            return ArkIdentityConnectorInfo.model_validate(query_result['Result']["Results"][0]['Row'])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to retrieve identity connector by id [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to retrieve identity connector by id [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
