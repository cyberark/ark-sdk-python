from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Any, Final, Optional

from overrides import overrides

from ark_sdk_python.common.connections.ark_connection import ArkConnection
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionDetails, ArkConnectionResult

SSH_PORT: Final[int] = 22


class ArkSSHConnection(ArkConnection):
    def __init__(self):
        super().__init__()
        self.__is_connected: bool = False
        self.__is_suspended: bool = False
        self.__ssh_client: Optional[Any] = None

    @overrides
    def connect(self, connection_details: ArkConnectionDetails) -> None:
        """
        Performs SSH connection with given details or keys
        Saves the ssh session to be used for command executions

        Args:
            connection_details (ArkConnectionDetails): _description_

        Raises:
            ArkException: _description_
        """
        import paramiko

        if self.__is_connected:
            return
        try:
            target_port = SSH_PORT
            user = None
            password = None
            private_key_data = None
            private_key = None
            if connection_details.port:
                target_port = connection_details.port
            if connection_details.credentials:
                user = connection_details.credentials.user
                if connection_details.credentials.password:
                    password = connection_details.credentials.password.get_secret_value()
                elif connection_details.credentials.private_key_filepath:
                    path = Path(connection_details.credentials.private_key_filepath)
                    if not path.exists():
                        raise ArkException(f'Given private key path [{path}] does not exist')
                    private_key_data = path.read_text(encoding='utf-8')
                elif connection_details.credentials.private_key_contents:
                    private_key_data = connection_details.credentials.private_key_contents
                if private_key_data:
                    private_key_io = StringIO(private_key_data)
                    private_key = paramiko.RSAKey.from_private_key(private_key_io)
                    private_key_io.close()
            self.__ssh_client = paramiko.SSHClient()
            self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh_client.connect(
                hostname=connection_details.address, port=target_port, username=user, password=password, pkey=private_key
            )
            self.__is_connected = True
            self.__is_suspended = False
        except Exception as ex:
            raise ArkException(f'Failed to ssh connect [{str(ex)}]') from ex

    @overrides
    def disconnect(self) -> None:
        """
        Disconnects the ssh session
        """
        if not self.__is_connected:
            return
        self.__ssh_client.close()
        self.__ssh_client = None
        self.__is_connected = False
        self.__is_suspended = False

    @overrides
    def suspend_connection(self) -> None:
        """
        Suspends execution of ssh commands
        """
        self.__is_suspended = True

    @overrides
    def restore_connection(self) -> None:
        """
        Restores execution of ssh commands
        """
        self.__is_suspended = False

    @overrides
    def is_suspended(self) -> bool:
        """
        Checks whether ssh commands can be executed or not

        Returns:
            bool: _description_
        """
        return self.__is_suspended

    @overrides
    def is_connected(self) -> bool:
        """
        Checks whether theres a ssh session connected

        Returns:
            bool: _description_
        """
        return self.__is_connected

    @overrides
    def run_command(self, command: ArkConnectionCommand) -> ArkConnectionResult:
        """
        Runs a command over ssh session, returning the result accordingly

        Args:
            command (ArkConnectionCommand): _description_

        Raises:
            ArkException: _description_

        Returns:
            ArkConnectionResult: _description_
        """
        if not self.__is_connected or self.__is_suspended:
            raise ArkException('Cannot run command while not being connected')
        self._logger.debug(f'Running command [{command.command}]')
        _, stdout_stream, stderr_stream = self.__ssh_client.exec_command(command=command.command)
        rc = stdout_stream.channel.recv_exit_status()
        stdout = ''.join(stdout_stream.readlines())
        stderr = ''.join(stderr_stream.readlines())
        if rc != command.expected_rc and command.raise_on_error:
            raise ArkException(f'Failed to execute command [{command.command}] - [{rc}] - [{stderr}]')
        self._logger.debug(f'Command rc: [{rc}]')
        self._logger.debug(f'Command stdout: [{stdout}]')
        self._logger.debug(f'Command stderr: [{stderr}]')
        return ArkConnectionResult(stdout=stdout, stderr=stderr, rc=rc)
