import json
import subprocess
import time
from http import HTTPStatus
from typing import Dict, Final, Iterator, List, Optional, Set, Tuple

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkAsyncRequest, ArkPage
from ark_sdk_python.common.connections import ArkConnection
from ark_sdk_python.common.connections.ssh import SSH_PORT, ArkSSHConnection
from ark_sdk_python.common.connections.winrm import WINRM_HTTPS_PORT, ArkWinRMConnection
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkException, ArkServiceException
from ark_sdk_python.models.common import ArkAsyncRequestSettings, ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionCredentials, ArkConnectionDetails, ArkConnectionType
from ark_sdk_python.models.common.connections.connection_data import ArkSSHConnectionData, ArkWinRMConnectionData
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.access import (
    ArkSIAConnector,
    ArkSIAConnectorHealth,
    ArkSIAConnectorSetupScript,
    ArkSIAConnectorsFilter,
    ArkSIAConnectorsStats,
    ArkSIADeleteConnector,
    ArkSIADeleteHttpsRelay,
    ArkSIAGetConnector,
    ArkSIAGetConnectorSetupScript,
    ArkSIAGetHttpsRelay,
    ArkSIAGetHttpsRelaySetupScript,
    ArkSIAHttpsRelay,
    ArkSIAHttpsRelaySetupScript,
    ArkSIAHttpsRelaysFilter,
    ArkSIAInstallConnector,
    ArkSIAInstallRelay,
    ArkSIARotateConnector,
    ArkSIARotateHttpsRelay,
    ArkSIATestConnectorReachability,
    ArkSIAUninstallConnector,
    ArkSIAUpgradeConnector,
    ArkSIAUpgradeConnectorAsyncTask,
    ArkSIAUpgradeHttpsRelay,
    serialize_access_workspace_type,
)
from ark_sdk_python.models.services.sia.access.ark_sia_test_connector_reachability import ArkSIATestConnectorReachabilityResponse
from ark_sdk_python.models.services.sia.access.ark_sia_uninstall_relay import ArkSIAUninstallRelay
from ark_sdk_python.models.services.sia.access.ark_sia_update_connector_maintenance_mode import ArkSIAUpdateMaintenanceMode
from ark_sdk_python.services.ark_service import ArkService
from ark_sdk_python.services.sia.access.ark_sia_upgrade_connector_async_request import ArkSIAUpgradeConnectorAsyncRequest

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-access', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
CONNECTORS_API: Final[str] = 'api/connectors'
PREV_CONNECTORS_API: Final[str] = 'api/connectors?version=4'
CONNECTORS_SETUP_SCRIPT_API: Final[str] = 'api/connectors/setup-script'
CONNECTOR_API: Final[str] = 'api/connectors/{connector_id}'
UPGRADE_CONNECTOR_API: Final[str] = 'api/connectors/{connector_id}/upgrade'
ROTATE_CONNECTOR_API: Final[str] = 'api/connectors/{connector_id}/rotate'
TEST_CONNECTOR_REACHABILITY_API: Final[str] = 'api/connectors/{connector_id}/reachability'
CONNECTOR_MAINTENANCE_API: Final[str] = 'api/connectors/{connector_id}/maintenance'
HTTPS_RELAYS_API: Final[str] = 'api/https-relays'
HTTPS_RELAY_API: Final[str] = 'api/https-relays/{https_relay_id}'
HTTPS_RELAY_SETUP_SCRIPT_API: Final[str] = 'api/https-relays/setup-script'
UPGRADE_HTTPS_RELAY_API: Final[str] = 'api/https-relays/{https_relay_id}/upgrade'
ROTATE_HTTPS_RELAY_API: Final[str] = 'api/https-relays/{https_relay_id}/rotate'

# Linux / Darwin Commands
UNIX_STOP_CONNECTOR_SERVICE_CMD: Final[str] = 'sudo systemctl stop cyberark-dpa-connector'
UNIX_REMOVE_CONNECTOR_SERVICE_CMD: Final[str] = (
    'sudo rm -f /etc/systemd/system/cyberark-dpa-connector.service && sudo rm -f /usr/lib/systemd/system/cyberark-dpa-connector.service && sudo systemctl daemon-reload && sudo systemctl reset-failed'
)
UNIX_REMOVE_CONNECTOR_FILES_CMD: Final[str] = 'sudo rm -rf /opt/cyberark/connector'
UNIX_CONNECTOR_ACTIVE_CMD: Final[str] = 'sudo systemctl is-active --quiet cyberark-dpa-connector'
UNIX_READ_CONNECTOR_CONFIG_CMD: Final[str] = 'sudo cat /opt/cyberark/connector/connector.config.json'

# Windows Commands
WIN_STOP_CONNECTOR_SERVICE_CMD: Final[str] = 'Stop-Service -Name \"CyberArkDPAConnector\"'
WIN_REMOVE_CONNECTOR_SERVICE_CMD: Final[str] = """$service = Get-WmiObject -Class Win32_Service -Filter "Name='CyberArkDPAConnector'"
$service.delete()
"""
WIN_REMOVE_CONNECTOR_FILES_CMD: Final[str] = 'Remove-Item -LiteralPath \"C:\\Program Files\\CyberArk\\DPAConnector\" -Force -Recurse'
WIN_CONNECTOR_ACTIVE_CMD: Final[str] = """$result = Get-Service -Name \"CyberArkDPAConnector\"
if ($result.Status -ne 'Running')
{
    return 1
}
"""
WIN_READ_CONNECTOR_CONFIG_CMD: Final[str] = 'Get-Content -Path \"C:\\Program Files\\CyberArk\\DPAConnector\\connector.config.json\"'

CONNECTOR_CMDSET: Final[Dict[ArkOsType, Dict[str, str]]] = {
    ArkOsType.LINUX: {
        'stop-connector-service': UNIX_STOP_CONNECTOR_SERVICE_CMD,
        'remove-connector-service': UNIX_REMOVE_CONNECTOR_SERVICE_CMD,
        'remove-connector-files': UNIX_REMOVE_CONNECTOR_FILES_CMD,
        'connector-active': UNIX_CONNECTOR_ACTIVE_CMD,
        'read-connector-config': UNIX_READ_CONNECTOR_CONFIG_CMD,
    },
    ArkOsType.WINDOWS: {
        'stop-connector-service': WIN_STOP_CONNECTOR_SERVICE_CMD,
        'remove-connector-service': WIN_REMOVE_CONNECTOR_SERVICE_CMD,
        'remove-connector-files': WIN_REMOVE_CONNECTOR_FILES_CMD,
        'connector-active': WIN_CONNECTOR_ACTIVE_CMD,
        'read-connector-config': WIN_READ_CONNECTOR_CONFIG_CMD,
    },
}
CONNECTOR_CMDSET[ArkOsType.DARWIN] = CONNECTOR_CMDSET[ArkOsType.LINUX]
CONNECTOR_READY_RETRY_COUNT: Final[int] = 5
CONNECTOR_RETRY_TICK_SECONDS: Final[int] = 3.0

# Linux / Darwin Relay Commands
UNIX_STOP_RELAY_SERVICE_CMD: Final[str] = 'sudo systemctl stop cyberark-sia-https-relay'
UNIX_REMOVE_RELAY_SERVICE_CMD: Final[str] = (
    'sudo rm -f /etc/systemd/system/cyberark-sia-https-relay.service && sudo rm -f /usr/lib/systemd/system/cyberark-sia-https-relay.service && sudo systemctl daemon-reload && sudo systemctl reset-failed'
)
UNIX_REMOVE_RELAY_FILES_CMD: Final[str] = 'sudo rm -rf /opt/cyberark-relay'
UNIX_RELAY_ACTIVE_CMD: Final[str] = 'sudo systemctl is-active --quiet cyberark-sia-https-relay'
UNIX_READ_RELAY_CONFIG_CMD: Final[str] = 'sudo cat /opt/cyberark-relay/https-relay/https-relay.config.json'

# Windows Relay Commands
WIN_STOP_RELAY_SERVICE_CMD: Final[str] = 'Stop-Service -Name \"CyberArkSIAHttpsRelay\"'
WIN_REMOVE_RELAY_SERVICE_CMD: Final[str] = """$service = Get-WmiObject -Class Win32_Service -Filter "Name='CyberArkSIAHttpsRelay'"
$service.delete()
"""
WIN_REMOVE_RELAY_FILES_CMD: Final[str] = 'Remove-Item -LiteralPath \"C:\\Program Files\\CyberArk\\SIAHttpsRelay\" -Force -Recurse'
WIN_RELAY_ACTIVE_CMD: Final[str] = """$result = Get-Service -Name \"CyberArkSIAHttpsRelay\"
if ($result.Status -ne 'Running')
{
    return 1
}
"""
WIN_READ_RELAY_CONFIG_CMD: Final[str] = 'Get-Content -Path \"C:\\Program Files\\CyberArk\\SIAHttpsRelay\\https-relay.config.json\"'

RELAY_CMDSET: Final[Dict[ArkOsType, Dict[str, str]]] = {
    ArkOsType.LINUX: {
        'stop-relay-service': UNIX_STOP_RELAY_SERVICE_CMD,
        'remove-relay-service': UNIX_REMOVE_RELAY_SERVICE_CMD,
        'remove-relay-files': UNIX_REMOVE_RELAY_FILES_CMD,
        'relay-active': UNIX_RELAY_ACTIVE_CMD,
        'read-relay-config': UNIX_READ_RELAY_CONFIG_CMD,
    },
    ArkOsType.WINDOWS: {
        'stop-relay-service': WIN_STOP_RELAY_SERVICE_CMD,
        'remove-relay-service': WIN_REMOVE_RELAY_SERVICE_CMD,
        'remove-relay-files': WIN_REMOVE_RELAY_FILES_CMD,
        'relay-active': WIN_RELAY_ACTIVE_CMD,
        'read-relay-config': WIN_READ_RELAY_CONFIG_CMD,
    },
}
RELAY_CMDSET[ArkOsType.DARWIN] = RELAY_CMDSET[ArkOsType.LINUX]
RELAY_READY_RETRY_COUNT: Final[int] = 10
RELAY_RETRY_TICK_SECONDS: Final[float] = 3.0

# Fixed helm release name used for K8s ephemeral connector deployments
K8S_EPHEMERAL_HELM_RELEASE_NAME: Final[str] = 'sia-connector'

ArkSIAHttpsRelaysPage = ArkPage[ArkSIAHttpsRelay]


class ArkSIAAccessService(ArkService):
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
            connection = ArkSSHConnection()
            connection_details = ArkConnectionDetails(
                address=target_machine,
                port=SSH_PORT,
                connection_type=ArkConnectionType.SSH,
                credentials=ArkConnectionCredentials(
                    user=username, password=password, private_key_filepath=private_key_path, private_key_contents=private_key_contents
                ),
                connection_data=ArkSSHConnectionData(),
            )
        connection.connect(connection_details)
        return connection, CONNECTOR_CMDSET[os_type]

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
        connection.run_command(ArkConnectionCommand(command=cmdset['stop-connector-service'], raise_on_error=False))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-service'], raise_on_error=False))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-files'], raise_on_error=False))
        if os_type == ArkOsType.WINDOWS:
            connection.run_command(ArkConnectionCommand(command=install_script, extra_command_data={'force_command_split': True}))
        else:
            connection.run_command(ArkConnectionCommand(command=install_script))
        retry_count = CONNECTOR_READY_RETRY_COUNT
        while True:
            try:
                connection.run_command(ArkConnectionCommand(command=cmdset['connector-active']))
                break
            except ArkException as ex:
                self._logger.exception(f'Failed to check whether a connector is active [{str(ex)}]')
                if retry_count > 0:
                    retry_count = retry_count - 1
                    self._logger.info(
                        f'Retrying to check if connector is active, sleeping for '
                        f'[{CONNECTOR_RETRY_TICK_SECONDS}] and retrying, retries left [{retry_count}]'
                    )
                    time.sleep(CONNECTOR_RETRY_TICK_SECONDS)
                    continue
                raise
        result = connection.run_command(ArkConnectionCommand(command=cmdset['read-connector-config']))
        connector_config = json.loads(str(result.stdout).strip())
        return connector_config['Id']

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
        connection.run_command(ArkConnectionCommand(command=cmdset['stop-connector-service']))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-service']))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-connector-files']))

    def __install_k8s_ephemeral_connector(self, install_script: str) -> None:
        """
        Runs the setup script locally (rather than over SSH/WinRM to a target machine). The script is already
        fully configured by the backend, since the K8s details were sent as part of the setup-script API
        request, so it is run as-is.
        """
        self._logger.info('Running K8s ephemeral connector setup script locally')
        result = subprocess.run(install_script, shell=True, check=False)  # nosec
        if result.returncode != 0:
            raise ArkServiceException(f'Failed to run K8s ephemeral connector setup script, exit code [{result.returncode}]')

    def __uninstall_k8s_ephemeral_connector(self, namespace: str) -> None:
        """
        Uninstalls a K8s ephemeral connector directly via helm, using the fixed K8S_EPHEMERAL_HELM_RELEASE_NAME
        as the helm release name.
        """
        self._logger.info(f'Uninstalling K8s ephemeral connector [{K8S_EPHEMERAL_HELM_RELEASE_NAME}] via helm from namespace [{namespace}]')
        result = subprocess.run(['helm', 'uninstall', K8S_EPHEMERAL_HELM_RELEASE_NAME, '--namespace', namespace], check=False)  # nosec
        if result.returncode != 0:
            raise ArkServiceException(f'Failed to uninstall K8s ephemeral connector via helm, exit code [{result.returncode}]')

    def list_all_connectors(self) -> List[ArkSIAConnector]:
        """
        Lists all existing connectors

        Raises:
            ArkServiceException: _description_
            ArkServiceException: _description_

        Returns:
            List[ArkSIAConnector]: _description_
        """
        self._logger.info('Listing all connectors')
        resp: Response = self.__client.get(PREV_CONNECTORS_API)
        if resp.status_code == HTTPStatus.OK:
            try:
                print(resp.json())
                return TypeAdapter(List[ArkSIAConnector]).validate_python(resp.json()['items'])
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse list connectors response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list connectors response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list connectors [{resp.text}] - [{resp.status_code}]')

    def list_connectors(self) -> List[ArkSIAConnectorHealth]:
        """
        Lists all existing connectors

        Raises:
            ArkServiceException: _description_
            ArkServiceException: _description_

        Returns:
            List[ArkSIAConnectorHealth]: _description_
        """
        self._logger.info('Listing all connectors')
        resp: Response = self.__client.get(CONNECTORS_API)
        if resp.status_code == HTTPStatus.OK:
            try:
                validated = TypeAdapter(List[ArkSIAConnectorHealth]).validate_python(resp.json()['items'])
                return [item.model_dump(by_alias=True) for item in validated]
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse list connectors response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list connectors response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list connectors [{resp.text}] - [{resp.status_code}]')

    def list_connectors_by(self, connectors_filter: ArkSIAConnectorsFilter) -> List[ArkSIAConnector]:
        """
        Lists connectors by given filter

        Args:
            connectors_filter (ArkSIAConnectorsFilter): _description_

        Returns:
            List[ArkSIAConnector]: _description_
        """
        self._logger.info(f'Listing connectors by filter [{connectors_filter}]')
        connectors = self.list_all_connectors()

        # Filter by accounts
        if connectors_filter.accounts:
            connectors = [c for c in connectors if c.account and c.account in connectors_filter.accounts]

        # Filter by regions
        if connectors_filter.regions:
            connectors = [c for c in connectors if c.region and c.region in connectors_filter.regions]

        # Filter by host types
        if connectors_filter.host_types:
            connectors = [c for c in connectors if c.connector_host_type in connectors_filter.host_types]

        # Filter only upgradable connectors
        if connectors_filter.only_upgradable_connectors:
            connectors = [c for c in connectors if c.is_upgradable and not c.is_latest_version]

        # Filter only latest version connectors
        if connectors_filter.only_latest_version_connectors:
            connectors = [c for c in connectors if c.is_latest_version]

        # Filter only connectors with active sessions
        if connectors_filter.only_connectors_with_sessions:
            connectors = [c for c in connectors if c.active_sessions_count > 0]

        # Filter by status codes
        if connectors_filter.status_codes:
            connectors = [c for c in connectors if c.status_code.name in connectors_filter.status_codes]

        # Filter by os types
        if connectors_filter.os_types:
            connectors = [c for c in connectors if c.connector_os in connectors_filter.os_types]

        return connectors

    def delete_connector(self, delete_connector: ArkSIADeleteConnector) -> None:
        """
        Deletes a given connector from the backend database
        If uninstallation of the connector is also requested, connects and uninstalls the connector from the machine

        Args:
            delete_connector (ArkSIADeleteConnector): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting connector [{delete_connector.connector_id}]')
        if delete_connector.uninstall_connector:
            self.uninstall_connector(
                ArkSIAUninstallConnector(
                    connector_id=delete_connector.connector_id,
                    username=delete_connector.username,
                    target_machine=delete_connector.target_machine,
                    password=delete_connector.password,
                    private_key_path=delete_connector.private_key_path,
                    private_key_contents=delete_connector.private_key_contents,
                )
            )

        params = {}
        if delete_connector.force_delete is not None:
            params['force_delete'] = str(delete_connector.force_delete).lower()
        resp: Response = self.__client.delete(
            CONNECTOR_API.format(connector_id=delete_connector.connector_id), params=params if params else None
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to delete connector [{resp.text}] - [{resp.status_code}]')

    def upgrade_connector(self, upgrade_connector: ArkSIAUpgradeConnector) -> ArkAsyncRequest:
        """
        Upgrades a connector if upgradable, an exception is thrown if an error happens or the connector is not upgradable
        Once the upgrade starts, an async request is returned to be polled

        Args:
            upgrade_connector (ArkSIAUpgradeConnector): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAsyncRequest: _description_
        """

        resp: Response = self.__client.post(UPGRADE_CONNECTOR_API.format(connector_id=upgrade_connector.connector_id))
        if resp.status_code == HTTPStatus.OK:
            req = ArkSIAUpgradeConnectorAsyncRequest(
                self.__client,
                ArkSIAUpgradeConnectorAsyncTask(
                    task_id=upgrade_connector.connector_id,
                    connector=self.connector(ArkSIAGetConnector(connector_id=upgrade_connector.connector_id)),
                ),
                async_request_settings=ArkAsyncRequestSettings(
                    poll_allow_refreshable_connection=upgrade_connector.poll_allow_refreshable_connection
                ),
            )
            if upgrade_connector.poll:
                req.poll(upgrade_connector.poll_timeout_seconds, upgrade_connector.poll_progress_callback)
            return req
        raise ArkServiceException(f'Failed to upgrade connector [{resp.text}] - [{resp.status_code}]')

    def rotate_connector(self, rotate_connector: ArkSIARotateConnector) -> None:
        """
        Triggers certificate rotation for a connector

        Args:
            rotate_connector (ArkSIARotateConnector): Request containing the connector ID to rotate

        Raises:
            ArkServiceException: Raised when the rotation request fails
        """
        self._logger.info(f'Rotating connector [{rotate_connector.connector_id}]')
        resp: Response = self.__client.post(ROTATE_CONNECTOR_API.format(connector_id=rotate_connector.connector_id))
        if resp.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to rotate connector [{resp.text}] - [{resp.status_code}]')

    def test_connector_reachability(
        self, test_connector_reachability: ArkSIATestConnectorReachability
    ) -> ArkSIATestConnectorReachabilityResponse:
        """
        Tests reachability to backend endpoints and target hostname/port from specified connector

        Args:
            test_connector_reachability (ArkSIATestConnectorReachability): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            Reachability test result: _description_
        """
        body = {
            'checkBackendEndpoints': test_connector_reachability.check_backend_endpoints,
        }
        if test_connector_reachability.target_hostname and test_connector_reachability.target_port:
            body['targets'] = [{'hostname': test_connector_reachability.target_hostname, 'port': test_connector_reachability.target_port}]
        resp: Response = self.__client.post(
            TEST_CONNECTOR_REACHABILITY_API.format(connector_id=test_connector_reachability.connector_id),
            json=body,
        )
        if resp.status_code == HTTPStatus.OK:
            return ArkSIATestConnectorReachabilityResponse(**resp.json())
        raise ArkServiceException(f'Failed to test connector reachability [{resp.text}] - [{resp.status_code}]')

    def connector(self, get_connector: ArkSIAGetConnector) -> ArkSIAConnector:
        """
        Retrieves a connector by id

        Args:
            get_connector (ArkSIAGetConnector): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAConnector: _description_
        """
        self._logger.info(f'Retrieving connector [{get_connector.connector_id}]')
        resp: Response = self.__client.get(CONNECTOR_API.format(connector_id=get_connector.connector_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIAConnector.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse connector response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse connector response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve connector [{resp.text}] - [{resp.status_code}]')

    def connector_setup_script(self, get_connector_setup_script: ArkSIAGetConnectorSetupScript) -> ArkSIAConnectorSetupScript:
        """
        Retrieves a new connector installation setup script

        Args:
            get_connector_setup_script (ArkSIAGetConnectorSetupScript): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAConnectorSetupScript: _description_
        """
        self._logger.info('Retrieving new connector setup script')
        get_connector_setup_script_dict = get_connector_setup_script.model_dump(exclude_none=True)
        get_connector_setup_script_dict['connector_type'] = serialize_access_workspace_type(get_connector_setup_script.connector_type)
        resp: Response = self.__client.post(CONNECTORS_SETUP_SCRIPT_API, json=get_connector_setup_script_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkSIAConnectorSetupScript.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse connector setup script response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse connector setup script response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve connector setup script [{resp.text}] - [{resp.status_code}]')

    def install_connector(self, install_connector: ArkSIAInstallConnector) -> Optional[ArkSIAConnector]:
        """
        Gets a connector installation script
        Afterwards, installs a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Uses SSH on linux / darwin os type

        When install_connector.connector_os is k8s-ephemeral, there is no single target machine to connect
        to: the connector is a helm deployment that may run as multiple replicas, so the setup script
        (already configured server-side from install_connector.k8s_details, sent via the setup-script API
        call) is executed locally, and no connector is returned (the caller should look up the resulting
        connector(s) separately if needed).

        Args:
            install_connector (ArkSIAInstallConnector): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            Optional[ArkSIAConnector]: _description_
        """
        if install_connector.connector_os != ArkOsType.K8S_EPHEMERAL and (
            not install_connector.target_machine or not install_connector.username
        ):
            raise ArkServiceException(f'target_machine and username are required when connector_os is [{install_connector.connector_os}]')
        if install_connector.connector_os == ArkOsType.K8S_EPHEMERAL:
            self._logger.info('Installing K8s ephemeral connector by running the setup script locally')
        else:
            self._logger.info(
                f'Installing connector on machine [{install_connector.target_machine}] of type [{install_connector.connector_os}]'
            )
        installation_script = self.connector_setup_script(
            ArkSIAGetConnectorSetupScript(
                connector_os=install_connector.connector_os,
                connector_pool_id=install_connector.connector_pool_id,
                connector_type=install_connector.connector_type,
                k8s_details=install_connector.k8s_details,
            )
        )
        if install_connector.connector_os == ArkOsType.K8S_EPHEMERAL:
            self.__install_k8s_ephemeral_connector(installation_script.bash_cmd)
            return None
        connector_id = self.__install_connector_on_machine(
            install_script=installation_script.bash_cmd,
            os_type=install_connector.connector_os,
            target_machine=install_connector.target_machine,
            username=install_connector.username,
            password=install_connector.password.get_secret_value() if install_connector.password else None,
            private_key_path=install_connector.private_key_path,
            private_key_contents=(
                install_connector.private_key_contents.get_secret_value() if install_connector.private_key_contents else None
            ),
        )
        return self.connector(ArkSIAGetConnector(connector_id=connector_id))

    def uninstall_connector(self, uninstall_connector: ArkSIAUninstallConnector) -> None:
        """
        Uninstalls a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Uses SSH on linux / darwin os type

        When uninstall_connector.connector_os is k8s-ephemeral, there is no target machine to connect to and
        no single connector_id to remove from the platform, since a helm release can back multiple replica
        connectors: the connector(s) are instead uninstalled directly via
        'helm uninstall sia-connector --namespace <k8s_namespace>', and the platform records for ephemeral
        connectors self-expire once they stop checking in, so no delete_connector call is made.

        Args:
            uninstall_connector (ArkSIAUninstallConnector): _description_

        Raises:
            ArkServiceException: _description_
        """
        if uninstall_connector.connector_os == ArkOsType.K8S_EPHEMERAL:
            if not uninstall_connector.k8s_namespace:
                raise ArkServiceException(f'k8s_namespace is required when connector_os is [{uninstall_connector.connector_os}]')
            self._logger.info(
                f'Uninstalling K8s ephemeral connector(s) of type [{uninstall_connector.connector_os}] '
                f'from namespace [{uninstall_connector.k8s_namespace}]'
            )
            self.__uninstall_k8s_ephemeral_connector(uninstall_connector.k8s_namespace)
            return
        if not uninstall_connector.connector_id:
            raise ArkServiceException(f'connector_id is required when connector_os is [{uninstall_connector.connector_os}]')
        self._logger.info(f'Uninstalling connector [{uninstall_connector.connector_id}] from machine')
        connector = self.connector(ArkSIAGetConnector(connector_id=uninstall_connector.connector_id))
        self.__uninstall_connector_on_machine(
            connector.connector_os,
            uninstall_connector.target_machine or connector.connector_host_ip,
            uninstall_connector.username,
            uninstall_connector.password.get_secret_value() if uninstall_connector.password else None,
            uninstall_connector.private_key_path,
            uninstall_connector.private_key_contents,
        )

    def connectors_stats(self) -> ArkSIAConnectorsStats:
        """
        Calculates statistics on the connectors

        Returns:
            ArkSIAConnectorsStats: _description_
        """
        self._logger.info('Calculating connectors statistics')
        connectors = self.list_all_connectors()
        connectors_stats = ArkSIAConnectorsStats.model_construct()
        connectors_stats.connectors_count = len(connectors)
        connectors_stats.upgradable_connectors_count = len([c for c in connectors if c.is_upgradable])

        # Count connectors per os type
        os_types: Set[ArkOsType] = {c.connector_os for c in connectors}
        connectors_stats.connectors_count_by_os = {os: len([c for c in connectors if c.connector_os == os]) for os in os_types}

        # Count connectors per platform type
        platform_types: Set[ArkWorkspaceType] = {c.connector_host_type for c in connectors}
        connectors_stats.connectors_count_by_platform = {
            plat: len([c for c in connectors if c.connector_host_type == plat]) for plat in platform_types
        }

        # Count connectors per status codes
        status_code_types: Set[str] = {c.status_code.name for c in connectors}
        connectors_stats.connectors_count_by_status_codes = {
            sc: len([c for c in connectors if c.status_code.name == sc]) for sc in status_code_types
        }

        return connectors_stats

    def update_connector_maintenance_mode(
        self, update_connector_maintenance_mode: ArkSIAUpdateMaintenanceMode
    ) -> ArkSIAUpdateMaintenanceMode:
        """
        Updates a connector's maintenance mode

        Args:
            update_connector_maintenance_mode (ArkSIAUpdateMaintenanceMode): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAUpdateMaintenanceMode: _description_
        """
        self._logger.info(f'Updating maintenance mode for connector [{update_connector_maintenance_mode.connector_id}]')
        attempts = update_connector_maintenance_mode.retry_count
        delay_seconds = update_connector_maintenance_mode.retry_delay_seconds
        last_resp: Optional[Response] = None
        for attempt in range(1, attempts + 1):
            resp: Response = self.__client.put(
                CONNECTOR_MAINTENANCE_API.format(connector_id=update_connector_maintenance_mode.connector_id),
                json=update_connector_maintenance_mode.model_dump(by_alias=True),
            )
            last_resp = resp
            if resp.status_code == HTTPStatus.OK:
                return update_connector_maintenance_mode
            if attempt < attempts:
                self._logger.info(
                    f'Attempt {attempt}/{attempts} maintenance mode update failed with status {resp.status_code}, retrying in {delay_seconds} seconds'
                )
                time.sleep(delay_seconds)
                continue
            break
        if last_resp is not None:
            raise ArkServiceException(
                f'Failed to update connector maintenance mode [{last_resp.text}] - [{last_resp.status_code}] after [{attempts}] attempts'
            )
        raise ArkServiceException('Failed to update connector maintenance mode - request did not yield a response')

    def __list_relays_with_filters(self, relays_filter: Optional[ArkSIAHttpsRelaysFilter] = None) -> Iterator[ArkSIAHttpsRelaysPage]:
        continuation_token = None
        while True:
            params = {}
            if continuation_token:
                params['continuationToken'] = continuation_token
            resp: Response = self.__client.get(HTTPS_RELAYS_API, params=params if params else None)
            if resp.status_code == HTTPStatus.OK:
                try:
                    resp_json = resp.json()
                    relays = TypeAdapter(List[ArkSIAHttpsRelay]).validate_python(resp_json.get('items', []))
                    if relays_filter:
                        if relays_filter.only_latest_version_relays:
                            relays = [r for r in relays if r.is_latest_version]
                        if relays_filter.only_relays_with_sessions:
                            relays = [r for r in relays if r.active_sessions_count > 0]
                        if relays_filter.status_codes:
                            relays = [r for r in relays if r.status_code.name in relays_filter.status_codes]
                    yield ArkSIAHttpsRelaysPage(relays)
                    continuation_token = resp_json.get('continuationToken')
                    if not continuation_token:
                        break
                except (ValidationError, JSONDecodeError) as ex:
                    self._logger.exception(f'Failed to parse list HTTPS relays response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list HTTPS relays response [{str(ex)}] ') from ex
            else:
                raise ArkServiceException(f'Failed to list HTTPS relays [{resp.text}] - [{resp.status_code}]')

    def list_relays(self) -> Iterator[ArkSIAHttpsRelaysPage]:
        """
        Lists all existing HTTPS relays, yielding in pages until no continuation token
        is returned by the server.

        Raises:
            ArkServiceException: Raised when any page request fails or the response cannot be parsed

        Yields:
            Iterator[ArkSIAHttpsRelaysPage]: Pages of HTTPS relays
        """
        self._logger.info('Listing all HTTPS relays')
        yield from self.__list_relays_with_filters()

    def list_relays_by(self, https_relays_filter: ArkSIAHttpsRelaysFilter) -> Iterator[ArkSIAHttpsRelaysPage]:
        """
        Lists HTTPS relays by given filter, yielding in pages

        Args:
            https_relays_filter (ArkSIAHttpsRelaysFilter): Filter criteria

        Yields:
            Iterator[ArkSIAHttpsRelaysPage]: Pages of HTTPS relays matching the filter
        """
        self._logger.info(f'Listing HTTPS relays by filter [{https_relays_filter}]')
        yield from self.__list_relays_with_filters(https_relays_filter)

    def relay(self, get_https_relay: ArkSIAGetHttpsRelay) -> ArkSIAHttpsRelay:
        """
        Retrieves a single HTTPS relay by ID

        Args:
            get_https_relay (ArkSIAGetHttpsRelay): Request containing the HTTPS relay ID

        Raises:
            ArkServiceException: Raised when the relay is not found or response cannot be parsed

        Returns:
            ArkSIAHttpsRelay: The HTTPS relay details
        """
        self._logger.info(f'Retrieving HTTPS relay [{get_https_relay.https_relay_id}]')
        for page in self.__list_relays_with_filters():
            for relay in page:
                if relay.id == get_https_relay.https_relay_id:
                    return relay
        raise ArkServiceException(f'HTTPS relay [{get_https_relay.https_relay_id}] was not found')

    def delete_relay(self, delete_https_relay: ArkSIADeleteHttpsRelay) -> None:
        """
        Deletes an HTTPS relay by ID

        Args:
            delete_https_relay (ArkSIADeleteHttpsRelay): Request containing the HTTPS relay ID to delete

        Raises:
            ArkServiceException: Raised when the deletion fails
        """
        self._logger.info(f'Deleting HTTPS relay [{delete_https_relay.https_relay_id}]')
        if delete_https_relay.uninstall_relay:
            self.uninstall_relay(
                ArkSIAUninstallRelay(
                    https_relay_os=delete_https_relay.https_relay_os,
                    https_relay_id=delete_https_relay.https_relay_id,
                    username=delete_https_relay.username,
                    target_machine=delete_https_relay.target_machine,
                    password=delete_https_relay.password,
                    private_key_path=delete_https_relay.private_key_path,
                    private_key_contents=delete_https_relay.private_key_contents,
                )
            )
        params = {}
        if delete_https_relay.force_delete is not None:
            params['force_delete'] = str(delete_https_relay.force_delete).lower()
        resp: Response = self.__client.delete(
            HTTPS_RELAY_API.format(https_relay_id=delete_https_relay.https_relay_id), params=params if params else None
        )
        if resp.status_code not in (HTTPStatus.NO_CONTENT, HTTPStatus.OK):
            raise ArkServiceException(f'Failed to delete HTTPS relay [{resp.text}] - [{resp.status_code}]')

    def relay_setup_script(self, get_https_relay_setup_script: ArkSIAGetHttpsRelaySetupScript) -> ArkSIAHttpsRelaySetupScript:
        """
        Generates an HTTPS relay installation setup script

        Args:
            get_https_relay_setup_script (ArkSIAGetHttpsRelaySetupScript): Setup script parameters

        Raises:
            ArkServiceException: Raised when the request fails or response cannot be parsed

        Returns:
            ArkSIAHttpsRelaySetupScript: Contains the pre-signed script URL and the bash command to run
        """
        self._logger.info('Retrieving HTTPS relay setup script')
        setup_script_dict = get_https_relay_setup_script.model_dump(exclude_none=True)
        resp: Response = self.__client.post(HTTPS_RELAY_SETUP_SCRIPT_API, json=setup_script_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkSIAHttpsRelaySetupScript.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse HTTPS relay setup script response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse HTTPS relay setup script response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve HTTPS relay setup script [{resp.text}] - [{resp.status_code}]')

    def __install_relay_on_machine(
        self,
        install_script: str,
        os_type: ArkOsType,
        target_machine: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_contents: Optional[str] = None,
    ) -> str:
        connection, _ = self.__create_connection(os_type, target_machine, username, password, private_key_path, private_key_contents)
        cmdset = RELAY_CMDSET[os_type]
        connection.run_command(ArkConnectionCommand(command=cmdset['stop-relay-service'], raise_on_error=False))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-relay-service'], raise_on_error=False))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-relay-files'], raise_on_error=False))
        if os_type == ArkOsType.WINDOWS:
            connection.run_command(ArkConnectionCommand(command=install_script, extra_command_data={'force_command_split': True}))
        else:
            connection.run_command(ArkConnectionCommand(command=install_script))
        retry_count = RELAY_READY_RETRY_COUNT
        while True:
            try:
                connection.run_command(ArkConnectionCommand(command=cmdset['relay-active']))
                break
            except ArkException as ex:
                self._logger.exception(f'Failed to check whether an HTTPS relay is active [{str(ex)}]')
                if retry_count > 0:
                    retry_count = retry_count - 1
                    self._logger.info(
                        f'Retrying to check if HTTPS relay is active, sleeping for '
                        f'[{RELAY_RETRY_TICK_SECONDS}] and retrying, retries left [{retry_count}]'
                    )
                    time.sleep(RELAY_RETRY_TICK_SECONDS)
                    continue
                raise
        result = connection.run_command(ArkConnectionCommand(command=cmdset['read-relay-config']))
        relay_config = json.loads(str(result.stdout).strip())
        relay_id = relay_config.get('id') or relay_config.get('Id')
        if not relay_id:
            raise ArkServiceException('Failed to read HTTPS relay ID from relay configuration')
        return relay_id

    def install_relay(self, install_relay: ArkSIAInstallRelay) -> ArkSIAHttpsRelay:
        self._logger.info(f'Installing HTTPS relay on machine [{install_relay.target_machine}] of type [{install_relay.https_relay_os}]')
        installation_script = self.relay_setup_script(
            ArkSIAGetHttpsRelaySetupScript(
                https_relay_os=install_relay.https_relay_os,
                protocol_port_map=install_relay.protocol_port_map,
                expiration_minutes=install_relay.expiration_minutes,
                proxy_host=install_relay.proxy_host or '',
                proxy_port=install_relay.proxy_port,
                windows_installation_path=install_relay.windows_installation_path or '',
            )
        )
        relay_id = self.__install_relay_on_machine(
            install_script=installation_script.bash_cmd,
            os_type=install_relay.https_relay_os,
            target_machine=install_relay.target_machine,
            username=install_relay.username,
            password=install_relay.password.get_secret_value() if install_relay.password else None,
            private_key_path=install_relay.private_key_path,
            private_key_contents=(install_relay.private_key_contents.get_secret_value() if install_relay.private_key_contents else None),
        )
        return self.relay(ArkSIAGetHttpsRelay(https_relay_id=relay_id))

    def __uninstall_relay_on_machine(
        self,
        os_type: ArkOsType,
        target_machine: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_contents: Optional[str] = None,
    ) -> None:
        connection, _ = self.__create_connection(os_type, target_machine, username, password, private_key_path, private_key_contents)
        cmdset = RELAY_CMDSET[os_type]
        connection.run_command(ArkConnectionCommand(command=cmdset['stop-relay-service']))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-relay-service']))
        connection.run_command(ArkConnectionCommand(command=cmdset['remove-relay-files']))

    def uninstall_relay(self, uninstall_relay: ArkSIAUninstallRelay) -> None:
        """
        Uninstalls an HTTPS relay from its host machine by SSHing into it and removing the service and files.
        Does not delete the relay from the SIA service — use delete_relay for that.

        Args:
            uninstall_relay (ArkSIAUninstallRelay): Request containing the relay ID, OS type, and connection details

        Raises:
            ArkServiceException: Raised when the relay is not found or the relay host IP is unavailable
        """
        self._logger.info(f'Uninstalling HTTPS relay [{uninstall_relay.https_relay_id}] from machine')
        relay = self.relay(ArkSIAGetHttpsRelay(https_relay_id=uninstall_relay.https_relay_id))
        target_machine = uninstall_relay.target_machine or relay.host_ip
        if not target_machine:
            raise ArkServiceException(f'No target machine provided and HTTPS relay [{uninstall_relay.https_relay_id}] has no host IP')
        self.__uninstall_relay_on_machine(
            uninstall_relay.https_relay_os,
            target_machine,
            uninstall_relay.username,
            uninstall_relay.password.get_secret_value() if uninstall_relay.password else None,
            uninstall_relay.private_key_path,
            uninstall_relay.private_key_contents.get_secret_value() if uninstall_relay.private_key_contents else None,
        )

    def upgrade_relay(self, upgrade_https_relay: ArkSIAUpgradeHttpsRelay) -> None:
        """
        Triggers an upgrade for an HTTPS relay

        Args:
            upgrade_https_relay (ArkSIAUpgradeHttpsRelay): Request containing the HTTPS relay ID to upgrade

        Raises:
            ArkServiceException: Raised when the upgrade request fails
        """
        self._logger.info(f'Upgrading HTTPS relay [{upgrade_https_relay.https_relay_id}]')
        resp: Response = self.__client.post(UPGRADE_HTTPS_RELAY_API.format(https_relay_id=upgrade_https_relay.https_relay_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to upgrade HTTPS relay [{resp.text}] - [{resp.status_code}]')

    def rotate_relay(self, rotate_https_relay: ArkSIARotateHttpsRelay) -> str:
        """
        Triggers certificate rotation for an HTTPS relay

        Args:
            rotate_https_relay (ArkSIARotateHttpsRelay): Request containing the HTTPS relay ID to rotate

        Raises:
            ArkServiceException: Raised when the rotation request fails

        Returns:
            str: Success message indicating the rotation has been initiated
        """
        self._logger.info(f'Rotating HTTPS relay [{rotate_https_relay.https_relay_id}]')
        resp: Response = self.__client.post(ROTATE_HTTPS_RELAY_API.format(https_relay_id=rotate_https_relay.https_relay_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to rotate HTTPS relay [{resp.text}] - [{resp.status_code}]')
        return 'Rotate Relay start successfully'

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
