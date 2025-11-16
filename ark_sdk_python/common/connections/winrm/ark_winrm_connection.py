import base64
import os
import uuid
from typing import Any, Final, Optional

from overrides import overrides

from ark_sdk_python.common.connections.ark_connection import ArkConnection
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionDetails, ArkConnectionResult

WINRM_HTTPS_PORT: Final[int] = 5986
IGNORE_CERT_VALIDATION_ENV_VAR: Final[str] = 'ARK_WINRM_NO_SSL_CERT_VALIDATION'


class ArkWinRMConnection(ArkConnection):
    def __init__(self):
        super().__init__()
        self.__is_connected: bool = False
        self.__is_suspended: bool = False
        self.__winrm_protocol: Optional[Any] = None
        self.__winrm_shell_id: Optional[str] = None

    @overrides
    def connect(self, connection_details: ArkConnectionDetails) -> None:
        """
        Performs WinRM connection with given details and certificate
        Saves the winrm protocol session and shell id to be used for command executions

        Args:
            connection_details (ArkConnectionDetails): _description_

        Raises:
            ArkException: _description_
        """
        import winrm

        if self.__is_connected:
            return
        try:
            target_port = WINRM_HTTPS_PORT
            user = None
            password = None
            cert = 'legacy_requests'
            if connection_details.port:
                target_port = connection_details.port
            if connection_details.credentials:
                user = connection_details.credentials.user
                if connection_details.credentials.password:
                    password = connection_details.credentials.password.get_secret_value()
            if connection_details.connection_data and connection_details.connection_data.certificate:
                cert = connection_details.connection_data.certificate
            server_cert_validation = 'validate'
            if len(os.getenv(IGNORE_CERT_VALIDATION_ENV_VAR, '')) > 0 or (
                connection_details.connection_data and not connection_details.connection_data.validate_certificate
            ):
                server_cert_validation = 'ignore'
            self.__winrm_protocol = winrm.Protocol(
                endpoint=f'https://{connection_details.address}:' f'{target_port}/wsman',
                transport='ntlm',
                username=user,
                password=password,
                ca_trust_path=cert,
                server_cert_validation=server_cert_validation,
                read_timeout_sec=10,
                operation_timeout_sec=5,
            )
            self.__winrm_shell_id = self.__winrm_protocol.open_shell()
            self.__is_connected = True
            self.__is_suspended = False
        except Exception as ex:
            raise ArkException(f'Failed to winrm connect [{str(ex)}]') from ex

    @overrides
    def disconnect(self) -> None:
        """
        Disconnects the winrm session
        """
        if not self.__is_connected:
            return
        self.__winrm_protocol.close_shell(self.__winrm_shell_id)
        self.__winrm_shell_id = None
        self.__winrm_protocol = None
        self.__is_connected = False
        self.__is_suspended = False

    @overrides
    def suspend_connection(self) -> None:
        """
        Suspends execution of winrm commands
        """
        self.__is_suspended = True

    @overrides
    def restore_connection(self) -> None:
        """
        Restores execution of winrm commands
        """
        self.__is_suspended = False

    @overrides
    def is_suspended(self) -> bool:
        """
        Checks whether winrm commands can be executed or not

        Returns:
            bool: _description_
        """
        return self.__is_suspended

    @overrides
    def is_connected(self) -> bool:
        """
        Checks whether theres a winrm session connected

        Returns:
            bool: _description_
        """
        return self.__is_connected

    @overrides
    def run_command(self, command: ArkConnectionCommand) -> ArkConnectionResult:
        """
        Runs a command over winrm session, returning the result accordingly

        Args:
            command (ArkConnectionCommand): _description_

        Raises:
            ArkException: _description_

        Returns:
            ArkConnectionResult: _description_
        """
        if not self.__is_connected or self.__is_suspended:
            raise ArkException('Cannot run command while not being connected')
        self._logger.debug(f'Running powershell command [{command.command}] of length [{len(command.command)}]')
        if len(command.command) > 2000 or (command.extra_command_data and command.extra_command_data.get('force_command_split', False)):
            encoded_command = command.command.encode('utf_16_le')
            max_size = 4000
            chunks = [encoded_command[i : i + max_size] for i in range(0, len(encoded_command), max_size)]
            command_unique_file_name = uuid.uuid4().hex
            command_file = f'"C:\\temp\\{command_unique_file_name}.ps1"'

            # Ensure C:\temp exists
            self.__winrm_protocol.run_command(self.__winrm_shell_id, 'if not exist "C:\\temp" mkdir C:\\temp')

            # Write chunks to the file
            for chunk in chunks:
                encoded_chunk_base64 = base64.b64encode(chunk).decode('ascii')
                command_id = self.__winrm_protocol.run_command(
                    self.__winrm_shell_id,
                    f'powershell -Command "[System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String(\'{encoded_chunk_base64}\')) | Add-Content -Path {command_file} -Encoding Unicode -NoNewline"',
                )
                stdout, stderr, rc = self.__winrm_protocol.get_command_output(self.__winrm_shell_id, command_id)

            # Execute the PowerShell script
            command_id = self.__winrm_protocol.run_command(self.__winrm_shell_id, f'powershell -File {command_file}')
            stdout, stderr, rc = self.__winrm_protocol.get_command_output(self.__winrm_shell_id, command_id)

            # Clean up the temporary file
            self.__winrm_protocol.run_command(self.__winrm_shell_id, f'del /f {command_file}')
        else:
            encoded_ps = f'powershell -encodedcommand {base64.b64encode(command.command.encode("utf_16_le")).decode("ascii")}'
            command_id: str = self.__winrm_protocol.run_command(self.__winrm_shell_id, encoded_ps.split()[0], encoded_ps.split()[1:])
            stdout, stderr, rc = self.__winrm_protocol.get_command_output(self.__winrm_shell_id, command_id)
        stdout = stdout.decode("utf8")
        stderr = stderr.decode("utf8")
        self.__winrm_protocol.cleanup_command(self.__winrm_shell_id, command_id)
        if command.expected_rc != rc and command.raise_on_error:
            raise ArkException(f'Failed to execute command [{command.command}] - [{rc}] - [{stderr}]')
        self._logger.debug(f'Command rc: [{rc}]')
        self._logger.debug(f'Command stdout: [{stdout}]')
        self._logger.debug(f'Command stderr: [{stderr}]')
        return ArkConnectionResult(stdout=stdout, stderr=stderr, rc=rc)
