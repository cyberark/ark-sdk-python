import itertools
import json
from http import HTTPStatus
from typing import Any, Dict, Final, Iterator, List, Optional, Set, Tuple, Type

from humps.main import camelize
from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkAsyncRequest, ArkPage
from ark_sdk_python.common.connections import ArkConnection
from ark_sdk_python.common.connections.winrm import WINRM_HTTPS_PORT, ArkWinRMConnection
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkNotSupportedException, ArkServiceException
from ark_sdk_python.models.common import ArkAsyncRequestSettings, ArkCountedValues, ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionCredentials, ArkConnectionDetails, ArkConnectionType
from ark_sdk_python.models.common.connections.connection_data import ArkWinRMConnectionData
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.cmgr import (
    ArkCmgrAddNetwork,
    ArkCmgrAddPool,
    ArkCmgrAddPoolBulkIdentifier,
    ArkCmgrAddPoolSingleIdentifier,
    ArkCmgrComponent,
    ArkCmgrComponentOperationAsyncTask,
    ArkCmgrComponentsFilter,
    ArkCmgrComponentsStats,
    ArkCmgrComponentStatusCode,
    ArkCmgrConnector,
    ArkCmgrConnectorComponentsFilter,
    ArkCmgrConnectorSetupScript,
    ArkCmgrConnectorsFilter,
    ArkCmgrConnectorsStats,
    ArkCmgrDeleteConnector,
    ArkCmgrDeleteNetwork,
    ArkCmgrDeletePool,
    ArkCmgrDeletePoolBulkIdentifier,
    ArkCmgrDeletePoolSingleIdentifier,
    ArkCmgrGetConnector,
    ArkCmgrGetConnectorComponent,
    ArkCmgrGetConnectorSetupScript,
    ArkCmgrGetNetwork,
    ArkCmgrGetPool,
    ArkCmgrGetPoolComponent,
    ArkCmgrInstallComponent,
    ArkCmgrInstallConnector,
    ArkCmgrListConnectorComponents,
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
    ArkCmgrReinstallComponent,
    ArkCmgrRescanComponents,
    ArkCmgrUninstallConnector,
    ArkCmgrUpdateNetwork,
    ArkCmgrUpdatePool,
    ArkCmgrUpgradeComponent,
    ArkCmgrUpgradeConnector,
    serialize_cmgr_workspace_type,
)
from ark_sdk_python.models.services.cmgr.ark_cmgr_bulk_response import ArkCmgrBulkResponses
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import MaintenanceOperationStatus
from ark_sdk_python.models.services.cmgr.ark_cmgr_uninstall_component import ArkCmgrUninstallComponent
from ark_sdk_python.services.ark_service import ArkService
from ark_sdk_python.services.cmgr.ark_cmgr_component_operation_async_request import ArkCmgrComponentOperationAsyncRequest

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='cmgr', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
CONNECTORS_API: Final[str] = 'api/connectors'
CONNECTOR_API: Final[str] = 'api/connectors/{connector_id}'
CONNECTOR_COMPONENTS_API: Final[str] = 'api/connectors/{connector_id}/components'
CONNECTOR_COMPONENT_API: Final[str] = 'api/connectors/{connector_id}/components/{component_id}'
REINSTALL_CONNECTOR_COMPONENT_API: Final[str] = 'api/connectors/{connector_id}/components/{component_id}/reinstall'
UPGRADE_CONNECTOR_COMPONENT_API: Final[str] = 'api/connectors/{connector_id}/components/{component_id}/upgrade'
RESCAN_CONNECTOR_COMPONENTS_API: Final[str] = 'api/connectors/{connector_id}/components/rescan'
UNINSTALL_CONNECTOR_COMPONENT_API: Final[str] = 'api/connectors/{connector_id}/components/{component_id}/uninstall'
COMPONENTS_API: Final[str] = 'api/components'
CONNECTORS_SETUP_SCRIPT_API: Final[str] = 'api/setup-script'
NETWORKS_API: Final[str] = 'api/pool-service/networks'
NETWORK_API: Final[str] = 'api/pool-service/networks/{network_id}'
POOLS_API: Final[str] = 'api/pool-service/pools'
POOL_API: Final[str] = 'api/pool-service/pools/{pool_id}'
POOL_IDENTIFIERS_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers'
POOL_IDENTIFIERS_BULK_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers-bulk'
POOL_IDENTIFIER_API: Final[str] = 'api/pool-service/pools/{pool_id}/identifiers/{identifier_id}'
POOLS_COMPONENTS_API: Final[str] = 'api/pool-service/pools/components'
POOL_COMPONENT_API: Final[str] = 'api/pool-service/pools/{pool_id}/components/{component_id}'

# Windows Commands
WIN_CONNECTOR_SERVICE_NAMES: Final[List[str]] = ['IdiraManagementAgent', 'CyberArkManagementAgent']
WIN_DETECT_CONNECTOR_SERVICE_CMD: Final[str] = (
    '$svc = Get-Service -Name "IdiraManagementAgent","CyberArkManagementAgent" -ErrorAction SilentlyContinue'
    ' | Select-Object -First 1\n'
    'if ($svc) { Write-Output $svc.Name } else { Write-Output "NONE" }'
)
WIN_STOP_CONNECTOR_SERVICE_CMD: Final[str] = 'Stop-Service -Name \"{service_name}\"'
WIN_REMOVE_CONNECTOR_SERVICE_CMD: Final[str] = """$service = Get-WmiObject -Class Win32_Service -Filter "Name='{service_name}'"
$service.delete()
"""
WIN_REMOVE_CONNECTOR_FILES_CMD: Final[str] = 'Remove-Item -LiteralPath \"C:\\Program Files\\CyberArk\\Management Agent\" -Force -Recurse'
WIN_CONNECTOR_ACTIVE_CMD: Final[str] = """$result = Get-Service -Name \"{service_name}\"
if ($result.Status -ne 'Running')
{{
    return 1
}}
"""
WIN_READ_CONNECTOR_CONFIG_CMD: Final[str] = 'Get-Content -Path \"C:\\Program Files\\CyberArk\\Management Agent\\client.id.json\"'

CONNECTOR_CMDSET: Final[Dict[ArkOsType, Dict[str, str]]] = {
    ArkOsType.WINDOWS: {
        'detect-connector-service': WIN_DETECT_CONNECTOR_SERVICE_CMD,
        'stop-connector-service': WIN_STOP_CONNECTOR_SERVICE_CMD,
        'remove-connector-service': WIN_REMOVE_CONNECTOR_SERVICE_CMD,
        'remove-connector-files': WIN_REMOVE_CONNECTOR_FILES_CMD,
        'connector-active': WIN_CONNECTOR_ACTIVE_CMD,
        'read-connector-config': WIN_READ_CONNECTOR_CONFIG_CMD,
    }
}

ArkCmgrConnectorsPage = ArkPage[ArkCmgrConnector]
ArkCmgrComponentsPage = ArkPage[ArkCmgrComponent]
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

    # pylint: disable=unused-argument
    def __create_connection(
        self,
        os_type: ArkOsType,
        target_machine: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_contents: Optional[str] = None,
    ) -> Tuple[ArkConnection, Dict[str, str]]:
        if os_type == ArkOsType.WINDOWS:
            connection = ArkWinRMConnection()
            connection_details = ArkConnectionDetails(
                address=target_machine,
                port=WINRM_HTTPS_PORT,
                connection_type=ArkConnectionType.WinRM,
                credentials=ArkConnectionCredentials(user=username, password=password),
                connection_data=ArkWinRMConnectionData(),
            )
        else:
            raise ArkNotSupportedException('Only windows connector mgmt type is supported')
        connection.connect(connection_details)
        return connection, CONNECTOR_CMDSET[os_type]

    def __detect_connector_service_name(self, connection: ArkConnection, cmdset: Dict[str, str]) -> Optional[str]:
        """
        Detects which management agent service name is installed on the machine.
        Returns the service name if found, or None if no service is present.
        """
        result = connection.run_command(ArkConnectionCommand(command=cmdset['detect-connector-service'], raise_on_error=False))
        detected = str(result.stdout).strip()
        if detected and detected != 'NONE':
            return detected
        return None

    def __install_connector_on_machine(
        self,
        install_script: str,
        os_type: ArkOsType,
        target_machine: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_contents: Optional[str] = None,
    ) -> str:
        connection, cmdset = self.__create_connection(os_type, target_machine, username, password, private_key_path, private_key_contents)
        existing_service = self.__detect_connector_service_name(connection, cmdset)
        if existing_service:
            connection.run_command(
                ArkConnectionCommand(command=cmdset['stop-connector-service'].format(service_name=existing_service), raise_on_error=False)
            )
            connection.run_command(
                ArkConnectionCommand(command=cmdset['remove-connector-service'].format(service_name=existing_service), raise_on_error=False)
            )
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-files'], raise_on_error=False))
        connection.run_command(ArkConnectionCommand(command=install_script))
        new_service = self.__detect_connector_service_name(connection, cmdset)
        if not new_service:
            raise ArkServiceException('Connector service not found after installation')
        connection.run_command(ArkConnectionCommand(command=cmdset['connector-active'].format(service_name=new_service)))
        result = connection.run_command(ArkConnectionCommand(command=cmdset['read-connector-config']))
        connector_config = json.loads(str(result.stdout).strip())
        return connector_config['thing_id']

    def __uninstall_connector_on_machine(
        self,
        os_type: ArkOsType,
        target_machine: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_contents: Optional[str] = None,
    ) -> None:
        connection, cmdset = self.__create_connection(os_type, target_machine, username, password, private_key_path, private_key_contents)
        service_name = self.__detect_connector_service_name(connection, cmdset)
        if service_name:
            connection.run_command(ArkConnectionCommand(command=cmdset['stop-connector-service'].format(service_name=service_name)))
            connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-service'].format(service_name=service_name)))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-files']))

    def __list_connectors_with_filters(
        self, connectors_filter: Optional[ArkCmgrConnectorsFilter] = None
    ) -> Iterator[ArkCmgrConnectorsPage]:
        url = CONNECTORS_API
        while True:
            params = connectors_filter.model_dump(by_alias=True) if connectors_filter else None
            if params and 'platformType' in params:
                params['platformType'] = serialize_cmgr_workspace_type(connectors_filter.platform_type)
            resp: Response = self.__client.get(url, params=params)
            if resp.status_code == HTTPStatus.OK:
                try:
                    result = resp.json()
                    yield ArkCmgrConnectorsPage(TypeAdapter(List[ArkCmgrConnector]).validate_python(result['connectors']))
                    if 'nextCursor' in result and result['nextCursor']:
                        url = result['nextCursor']
                    else:
                        break
                except (ValidationError, JSONDecodeError, KeyError) as ex:
                    self._logger.exception(f'Failed to parse list connectors response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list connectors response [{str(ex)}]') from ex
            else:
                raise ArkServiceException(f'Failed to list connectors [{resp.text}] - [{resp.status_code}]')

    def __list_components_with_filters(
        self, base_url: str, components_filter: Optional[ArkCmgrComponentsFilter] = None
    ) -> Iterator[ArkCmgrComponentsPage]:
        url = base_url
        while True:
            resp: Response = self.__client.get(
                url, params=components_filter.model_dump(by_alias=True, exclude={'connector_id'}) if components_filter else None
            )
            if resp.status_code == HTTPStatus.OK:
                try:
                    result = resp.json()
                    yield ArkCmgrConnectorsPage(TypeAdapter(List[ArkCmgrComponent]).validate_python(result['components']))
                    if 'nextCursor' in result and result['nextCursor']:
                        url = result['nextCursor']
                    else:
                        break
                except (ValidationError, JSONDecodeError, KeyError) as ex:
                    self._logger.exception(f'Failed to parse list components response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list components response [{str(ex)}]') from ex
            else:
                raise ArkServiceException(f'Failed to list components [{resp.text}] - [{resp.status_code}]')

    def list_connectors(self) -> Iterator[ArkCmgrConnectorsPage]:
        """
        Listing all connectors, yielding in pages

        Yields:
            Iterator[ArkCmgrConnectorsPage]: _description_
        """
        self._logger.info('Listing all connectors')
        yield from self.__list_connectors_with_filters()

    def list_connectors_by(self, connectors_filter: ArkCmgrConnectorsFilter) -> Iterator[ArkCmgrConnectorsPage]:
        """
        Listing connectors by filters, yielding in pages

        Args:
            connectors_filter (ArkCmgrConnectorsFilter): _description_

        Yields:
            Iterator[ArkCmgrConnectorsPage]: _description_
        """
        self._logger.info(f'Listing connectors by filter [{connectors_filter}]')
        yield from self.__list_connectors_with_filters(connectors_filter)

    def list_connector_components(self, list_connector_components: ArkCmgrListConnectorComponents) -> Iterator[ArkCmgrComponentsPage]:
        """
        Listing all specific connector components, yielding in pages

        Args:
            list_connector_components (ArkCmgrListConnectorComponents): _description_

        Yields:
            Iterator[ArkCmgrComponentsPage]: _description_
        """
        self._logger.info(f'Listing all connector [{list_connector_components.connector_id}] components')
        yield from self.__list_components_with_filters(CONNECTOR_COMPONENTS_API.format(connector_id=list_connector_components.connector_id))

    def list_connector_components_by(
        self, connector_components_filter: ArkCmgrConnectorComponentsFilter
    ) -> Iterator[ArkCmgrComponentsPage]:
        """
        Listing specific connector components by filters, yielding in pages

        Args:
            connector_components_filter (ArkCmgrConnectorComponentsFilter): _description_

        Yields:
            Iterator[ArkCmgrComponentsPage]: _description_
        """
        self._logger.info(
            f'Listing connector [{connector_components_filter.connector_id}] components by filter [{connector_components_filter}]'
        )
        yield from self.__list_components_with_filters(
            CONNECTOR_COMPONENTS_API.format(connector_id=connector_components_filter.connector_id), connector_components_filter
        )

    def list_components(self) -> Iterator[ArkCmgrComponentsPage]:
        """
        Listing all components, yielding in pages

        Yields:
            Iterator[ArkCmgrComponentsPage]: _description_
        """
        self._logger.info('Listing all components')
        yield from self.__list_components_with_filters(COMPONENTS_API)

    def list_components_by(self, components_filter: ArkCmgrComponentsFilter) -> Iterator[ArkCmgrComponentsPage]:
        """
        Listing components by filters, yielding in pages

        Args:
            components_filter (ArkCmgrComponentsFilter): _description_

        Yields:
            Iterator[ArkCmgrComponentsPage]: _description_
        """
        self._logger.info(f'Listing components by filter [{components_filter}]')
        yield from self.__list_components_with_filters(COMPONENTS_API, components_filter)

    def connector(self, get_connector: ArkCmgrGetConnector) -> ArkCmgrConnector:
        """
        Retrieves a connector by id

        Args:
            get_connector (ArkCmgrGetConnector): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrConnector: _description_
        """
        self._logger.info(f'Retrieving connector [{get_connector.connector_id}]')
        resp: Response = self.__client.get(CONNECTOR_API.format(connector_id=get_connector.connector_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrConnector.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse connector response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse connector response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve connector [{resp.text}] - [{resp.status_code}]')

    def connector_component(self, get_connector_component: ArkCmgrGetConnectorComponent) -> ArkCmgrComponent:
        """
        Retrieves a connector component by connector id and component id

        Args:
            get_connector_component (ArkCmgrGetConnectorComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrComponent: _description_
        """
        self._logger.info(
            f'Retrieving connector [{get_connector_component.connector_id}] ' f'component [{get_connector_component.component_id}]'
        )
        resp: Response = self.__client.get(
            CONNECTOR_COMPONENT_API.format(
                connector_id=get_connector_component.connector_id, component_id=get_connector_component.component_id
            )
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkCmgrComponent.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse connector component response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse connector component response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve connector component [{resp.text}] - [{resp.status_code}]')

    def rescan_components(self, rescan_components: ArkCmgrRescanComponents) -> None:
        """
        Triggers a rescanning of components on the connector host machine
        The rescanning is an async operation, which ends after a few seconds at most

        Args:
            rescan_components (ArkCmgrRescanComponents): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Triggering rescanning of components for connector [{rescan_components.connector_id}]')
        resp: Response = self.__client.post(RESCAN_CONNECTOR_COMPONENTS_API.format(connector_id=rescan_components.connector_id))
        if resp.status_code != HTTPStatus.ACCEPTED:
            raise ArkServiceException(f'Failed to trigger rescanning of components [{resp.text}] - [{resp.status_code}]')

    def delete_connector(self, delete_connector: ArkCmgrDeleteConnector) -> None:
        """
        Deletes a given connector from the backend database
        If uninstallation of the connector is also requested, connects and uninstalls the connector from the machine

        Args:
            delete_connector (ArkCmgrDeleteConnector): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting connector [{delete_connector.connector_id}]')
        if delete_connector.uninstall_connector:
            self.uninstall_connector(
                ArkCmgrUninstallConnector(
                    connector_id=delete_connector.connector_id,
                    username=delete_connector.username,
                    target_machine=delete_connector.target_machine,
                    password=delete_connector.password,
                    private_key_path=delete_connector.private_key_path,
                    private_key_contents=delete_connector.private_key_contents,
                )
            )

        resp: Response = self.__client.delete(CONNECTOR_API.format(connector_id=delete_connector.connector_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete connector [{resp.text}] - [{resp.status_code}]')

    def connector_setup_script(self, get_connector_setup_script: ArkCmgrGetConnectorSetupScript) -> ArkCmgrConnectorSetupScript:
        """
        Retrieves a new connector installation setup script

        Args:
            get_connector_setup_script (ArkCmgrGetConnectorSetupScript): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkCmgrConnectorSetupScript: _description_
        """
        from urlextract import URLExtract

        self._logger.info('Retrieving new connector setup script')
        get_connector_setup_script_data = get_connector_setup_script.model_dump(exclude_none=True)
        if not get_connector_setup_script.proxy_details or not get_connector_setup_script.proxy_details.proxy_address:
            if 'proxy_details' in get_connector_setup_script_data:
                del get_connector_setup_script_data['proxy_details']
        resp: Response = self.__client.post(CONNECTORS_SETUP_SCRIPT_API, json=get_connector_setup_script_data)
        if resp.status_code == HTTPStatus.OK:
            try:
                script = resp.json()['script']
                return ArkCmgrConnectorSetupScript(script=script, script_url=URLExtract().find_urls(script)[0])
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse connector setup script response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse connector setup script response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve connector setup script [{resp.text}] - [{resp.status_code}]')

    def install_connector(self, install_connector: ArkCmgrInstallConnector) -> ArkCmgrConnector:
        """
        Gets a connector installation script
        Afterwards, installs a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Linux / Darwin is not yet supported

        Args:
            install_connector (ArkCmgrInstallConnector): _description_

        Returns:
            ArkCmgrConnector: _description_
        """
        self._logger.info(f'Installing connector on machine [{install_connector.target_machine}] of type [{install_connector.os_type}]')
        installation_script = self.connector_setup_script(
            ArkCmgrGetConnectorSetupScript(
                os_type=install_connector.os_type,
                version=install_connector.version,
                installation_path=install_connector.installation_path,
                connector_pool_id=install_connector.connector_pool_id,
                proxy_details=install_connector.proxy_details,
            ),
        )
        connector_id = self.__install_connector_on_machine(
            install_script=installation_script.script,
            os_type=install_connector.os_type,
            target_machine=install_connector.target_machine,
            username=install_connector.username,
            password=install_connector.password.get_secret_value() if install_connector.password else None,
            private_key_path=install_connector.private_key_path,
            private_key_contents=(
                install_connector.private_key_contents.get_secret_value() if install_connector.private_key_contents else None
            ),
        )
        return self.connector(ArkCmgrGetConnector(connector_id=connector_id))

    def uninstall_component(self, uninstall_component: ArkCmgrUninstallComponent) -> ArkAsyncRequest:
        """
        Triggers an uninstall flow of a component on the connector machine via the CMS API.
        Returns an async request that can be polled until the uninstall completes or fails.

        Args:
            uninstall_component (ArkCmgrUninstallComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAsyncRequest: _description_
        """
        self._logger.info(f'Uninstalling component [{uninstall_component.component_id}] on connector [{uninstall_component.connector_id}]')
        body: Dict[str, Any] = {'extra_vars': uninstall_component.extra_vars or {}}
        resp: Response = self.__client.post(
            UNINSTALL_CONNECTOR_COMPONENT_API.format(
                connector_id=uninstall_component.connector_id,
                component_id=uninstall_component.component_id,
            ),
            json=body,
        )
        if resp.status_code == HTTPStatus.ACCEPTED:
            component = self.connector_component(
                ArkCmgrGetConnectorComponent(
                    connector_id=uninstall_component.connector_id,
                    component_id=uninstall_component.component_id,
                )
            )
            req = ArkCmgrComponentOperationAsyncRequest(
                client=self.__client,
                async_task=ArkCmgrComponentOperationAsyncTask(
                    task_id=uninstall_component.component_id,
                    component=component,
                    operation='UNINSTALL',
                ),
                async_request_settings=ArkAsyncRequestSettings(
                    poll_allow_refreshable_connection=uninstall_component.poll_allow_refreshable_connection,
                ),
            )
            if uninstall_component.poll:
                req.poll(uninstall_component.poll_timeout_seconds, uninstall_component.poll_progress_callback)
            return req
        raise ArkServiceException(f'Failed to uninstall component [{resp.text}] - [{resp.status_code}]')

    def uninstall_connector(self, uninstall_connector: ArkCmgrUninstallConnector) -> None:
        """
        Uninstalls a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Linux / Darwin is not yet supported

        Args:
            uninstall_connector (ArkCmgrUninstallConnector): _description_
        """
        self._logger.info(f'Uninstalling connector [{uninstall_connector.connector_id}] from machine')
        connector = self.connector(ArkCmgrGetConnector(connector_id=uninstall_connector.connector_id))
        self.__uninstall_connector_on_machine(
            connector.host.os,
            uninstall_connector.target_machine or connector.connector_host_ip,
            uninstall_connector.username,
            uninstall_connector.password.get_secret_value() if uninstall_connector.password else None,
            uninstall_connector.private_key_path,
            uninstall_connector.private_key_contents,
        )

    def install_component(self, install_component: ArkCmgrInstallComponent) -> ArkAsyncRequest:
        """
        Triggers an installation flow of a component on the connector machine
        The component will be installed async on the connector machine
        And an async request is returned to be polled untill the component is done installing

        Args:
            install_component (ArkCmgrInstallComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAsyncRequest: _description_
        """
        self._logger.info(f'Installing component [{install_component.component_name}] on connector [{install_component.connector_id}]')
        resp: Response = self.__client.post(
            CONNECTOR_COMPONENTS_API.format(connector_id=install_component.connector_id),
            json=install_component.model_dump(
                by_alias=True,
                exclude={'connector_id', 'poll', 'poll_timeout_seconds', 'poll_progress_callback', 'poll_allow_refreshable_connection'},
                exclude_none=True,
            ),
        )
        if resp.status_code == HTTPStatus.ACCEPTED:
            try:
                data = resp.json()
                component_id = None
                for key in ['component_id', 'job_id', 'operation_id', 'activity_id', 'task_id']:
                    if key in data:
                        component_id = data[key]
                        break
                    elif camelize(key) in data:
                        component_id = data[camelize(key)]
                        break
                if not component_id:
                    raise ArkServiceException(
                        f'Failed to install component, cannot find the response task id [{resp.text}] - [{resp.status_code}]'
                    )
                component = self.connector_component(
                    ArkCmgrGetConnectorComponent(connector_id=install_component.connector_id, component_id=component_id)
                )
                req = ArkCmgrComponentOperationAsyncRequest(
                    client=self.__client,
                    async_task=ArkCmgrComponentOperationAsyncTask(task_id=component_id, component=component, operation='INSTALL'),
                    async_request_settings=ArkAsyncRequestSettings(
                        poll_allow_refreshable_connection=install_component.poll_allow_refreshable_connection
                    ),
                )
                if install_component.poll:
                    req.poll(install_component.poll_timeout_seconds, install_component.poll_progress_callback)
                return req
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse component installation response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse component installation response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to install component [{resp.text}] - [{resp.status_code}]')

    def reinstall_component(self, reinstall_component: ArkCmgrReinstallComponent) -> ArkAsyncRequest:
        """
        Triggers a reinstallation flow of a component on the connector machine
        The component will be reinstalled async on the connector machine
        And an async request is returned to be polled untill the component is done reinstalling

        Args:
            reinstall_component (ArkCmgrReInstallComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAsyncRequest: _description_
        """
        self._logger.info(f'Reinstalling component [{reinstall_component.component_id}] on connector [{reinstall_component.connector_id}]')
        resp: Response = self.__client.post(
            REINSTALL_CONNECTOR_COMPONENT_API.format(
                connector_id=reinstall_component.connector_id, component_id=reinstall_component.component_id
            )
        )
        if resp.status_code == HTTPStatus.ACCEPTED:
            component = self.connector_component(
                ArkCmgrGetConnectorComponent(connector_id=reinstall_component.connector_id, component_id=reinstall_component.component_id)
            )
            req = ArkCmgrComponentOperationAsyncRequest(
                client=self.__client,
                async_task=ArkCmgrComponentOperationAsyncTask(
                    task_id=reinstall_component.component_id, component=component, operation='REINSTALL'
                ),
                async_request_settings=ArkAsyncRequestSettings(
                    poll_allow_refreshable_connection=reinstall_component.poll_allow_refreshable_connection
                ),
            )
            if reinstall_component.poll:
                req.poll(reinstall_component.poll_timeout_seconds, reinstall_component.poll_progress_callback)
            return req
        raise ArkServiceException(f'Failed to reinstall component [{resp.text}] - [{resp.status_code}]')

    def upgrade_component(self, upgrade_component: ArkCmgrUpgradeComponent) -> ArkAsyncRequest:
        """
        Triggers an upgrade flow of a component on the connector machine
        The component will be upgraded async on the connector machine
        And an async request is returned to be polled untill the component is done upgrading

        Args:
            upgrade_component (ArkCmgrUpgradeComponent): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAsyncRequest: _description_
        """
        self._logger.info(f'Upgrading component [{upgrade_component.component_id}] on connector [{upgrade_component.connector_id}]')
        resp: Response = self.__client.post(
            UPGRADE_CONNECTOR_COMPONENT_API.format(
                connector_id=upgrade_component.connector_id, component_id=upgrade_component.component_id
            ),
            json=upgrade_component.model_dump(
                by_alias=True,
                exclude={
                    'connector_id',
                    'component_id',
                    'poll',
                    'poll_timeout_seconds',
                    'poll_progress_callback',
                    'poll_allow_refreshable_connection',
                },
                exclude_none=True,
            ),
        )
        if resp.status_code == HTTPStatus.ACCEPTED:
            component = self.connector_component(
                ArkCmgrGetConnectorComponent(connector_id=upgrade_component.connector_id, component_id=upgrade_component.component_id)
            )
            req = ArkCmgrComponentOperationAsyncRequest(
                client=self.__client,
                async_task=ArkCmgrComponentOperationAsyncTask(
                    task_id=upgrade_component.component_id, component=component, operation='UPGRADE'
                ),
                async_request_settings=ArkAsyncRequestSettings(
                    poll_allow_refreshable_connection=upgrade_component.poll_allow_refreshable_connection
                ),
            )
            if upgrade_component.poll:
                req.poll(upgrade_component.poll_timeout_seconds, upgrade_component.poll_progress_callback)
            return req
        raise ArkServiceException(f'Failed to upgrade component [{resp.text}] - [{resp.status_code}]')

    def upgrade_connector(self, upgrade_connector: ArkCmgrUpgradeConnector) -> ArkAsyncRequest:
        """
        Triggers an upgrade flow of a connector on the connector machine
        The connector will be upgraded async on the connector machine
        And an async request is returned to be polled untill the connector is done upgrading

        Args:
            upgrade_connector (ArkCmgrUpgradeConnector): _description_

        Returns:
            ArkAsyncRequest: _description_
        """
        return self.upgrade_component(
            ArkCmgrUpgradeComponent(
                connector_id=upgrade_connector.connector_id,
                component_id=upgrade_connector.connector_id,
                poll=upgrade_connector.poll,
                poll_timeout_seconds=upgrade_connector.poll_timeout_seconds,
                poll_progress_callback=upgrade_connector.poll_progress_callback,
                poll_allow_refreshable_connection=upgrade_connector.poll_allow_refreshable_connection,
            )
        )

    def connectors_stats(self) -> ArkCmgrConnectorsStats:
        """
        Calculates connectors statistics

        Returns:
            ArkCmgrConnectorsStats: _description_
        """
        self._logger.info('Calculating connectors statistics')
        connectors = list(itertools.chain.from_iterable([p.items for p in list(self.list_connectors())]))
        connectors_stats = ArkCmgrConnectorsStats.model_construct()
        connectors_stats.connectors_count = len(connectors)

        # Get connectors count per status
        status_codes: Set[ArkCmgrComponentStatusCode] = {c.connector_status for c in connectors}
        connectors_stats.connectors_count_per_status = {sc: len([c for c in connectors if c.connector_status == sc]) for sc in status_codes}

        # Get connectors count per platform
        platform_types: Set[ArkWorkspaceType] = {c.platform_type for c in connectors}
        connectors_stats.connectors_count_per_platform = {
            pt: len([c for c in connectors if c.platform_type == pt]) for pt in platform_types
        }

        # Get connectors count per os
        os_types: Set[ArkOsType] = {c.host.os for c in connectors}
        connectors_stats.connectors_count_per_os = {ot: len([c for c in connectors if c.host.os == ot]) for ot in os_types}

        # Get upgradable connectors
        upgradable_connectors = [c.connector_id for c in connectors if c.upgrade_versions]
        connectors_stats.upgradable_connectors = ArkCountedValues(count=len(upgradable_connectors), values=upgradable_connectors)

        return connectors_stats

    def components_stats(self) -> ArkCmgrComponentsStats:
        """
        Calculates components statistics

        Returns:
            ArkCmgrComponentsStats: _description_
        """
        self._logger.info('Calculating components statistics')
        components = list(itertools.chain.from_iterable([p.items for p in list(self.list_components())]))
        components_stats = ArkCmgrComponentsStats.model_construct()
        components_stats.components_count = len(components)

        # Get components per connector
        connector_ids: Set[str] = {c.connector_id for c in components}
        components_per_connector = {cid: [c.component_name for c in components if c.connector_id == cid] for cid in connector_ids}
        components_stats.components_per_connector = {
            cid: ArkCountedValues(count=len(cmps), values=cmps) for cid, cmps in components_per_connector.items()
        }

        # Get connectors count per status
        status_codes: Set[ArkCmgrComponentStatusCode] = {c.component_status for c in components}
        components_stats.components_count_per_status = {sc: len([c for c in components if c.component_status == sc]) for sc in status_codes}

        # Get maintenanced components
        maintenanced_components = [
            c.component_id
            for c in components
            if c.maintenance_operation_details
            and c.maintenance_operation_details.status
            in [
                MaintenanceOperationStatus.PENDING,
                MaintenanceOperationStatus.RUNNING,
            ]
        ]
        components_stats.maintenanced_components = ArkCountedValues(count=len(maintenanced_components), values=maintenanced_components)

        # Get upgradable components
        upgradable_components = [c.component_id for c in components if c.upgrade_versions]
        components_stats.upgradable_components = ArkCountedValues(count=len(upgradable_components), values=upgradable_components)

        return components_stats

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
