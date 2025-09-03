import json
import time
from http import HTTPStatus
from typing import Dict, Final, Optional, Tuple

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.connections import ArkConnection
from ark_sdk_python.common.connections.ssh import SSH_PORT, ArkSSHConnection
from ark_sdk_python.common.connections.winrm import WINRM_HTTPS_PORT, ArkWinRMConnection
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkException, ArkServiceException
from ark_sdk_python.models.common import ArkOsType
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionCredentials, ArkConnectionDetails, ArkConnectionType
from ark_sdk_python.models.common.connections.connection_data import ArkSSHConnectionData, ArkWinRMConnectionData
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.access import (
    ArkSIAConnectorSetupScript,
    ArkSIAGetConnectorSetupScript,
    ArkSIAInstallConnector,
    ArkSIATestConnectorReachability,
    ArkSIAUninstallConnector,
    serialize_access_workspace_type,
)
from ark_sdk_python.models.services.sia.access.ark_sia_test_connector_reachability import ArkSIATestConnectorReachabilityResponse
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-access', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
CONNECTORS_SETUP_SCRIPT_API: Final[str] = 'api/connectors/setup-script'
TEST_CONNECTOR_REACHABILITY_API: Final[str] = 'api/connectors/{connector_id}/reachability'

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
WIN_REMOVE_CONNECTOR_SERVICE_CMD: Final[
    str
] = """$service = Get-WmiObject -Class Win32_Service -Filter "Name='CyberArkDPAConnector'"
$service.delete()
"""
WIN_REMOVE_CONNECTOR_FILES_CMD: Final[str] = 'Remove-Item -LiteralPath \"C:\\Program Files\\CyberArk\\DPAConnector\" -Force -Recurse'
WIN_CONNECTOR_ACTIVE_CMD: Final[
    str
] = """$result = Get-Service -Name \"CyberArkDPAConnector\"
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

    def install_connector(self, install_connector: ArkSIAInstallConnector) -> str:
        """
        Gets a connector installation script
        Afterwards, installs a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Uses SSH on linux / darwin os type

        Args:
            install_connector (ArkSIAInstallConnector): _description_

        Returns:
            str: _description_
        """
        self._logger.info(
            f'Installing connector on machine [{install_connector.target_machine}] of type [{install_connector.connector_os}]'
        )
        installation_script = self.connector_setup_script(
            ArkSIAGetConnectorSetupScript(
                connector_os=install_connector.connector_os,
                connector_pool_id=install_connector.connector_pool_id,
                connector_type=install_connector.connector_type,
            )
        )
        return self.__install_connector_on_machine(
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

    def uninstall_connector(self, uninstall_connector: ArkSIAUninstallConnector) -> None:
        """
        Uninstalls a connector on the remote machine based on the given parameters
        Uses WinRM on windows os type
        Uses SSH on linux / darwin os type

        Args:
            uninstall_connector (ArkSIAUninstallConnector): _description_
        """
        self._logger.info(f'Uninstalling connector [{uninstall_connector.connector_id}] from machine')
        self.__uninstall_connector_on_machine(
            uninstall_connector.connector_os,
            uninstall_connector.target_machine,
            uninstall_connector.username,
            uninstall_connector.password.get_secret_value() if uninstall_connector.password else None,
            uninstall_connector.private_key_path,
            uninstall_connector.private_key_contents,
        )

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
