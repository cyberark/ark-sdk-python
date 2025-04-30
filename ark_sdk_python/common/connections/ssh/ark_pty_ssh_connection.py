from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from overrides import overrides

from ark_sdk_python.common.connections.ark_connection import ArkConnection
from ark_sdk_python.common.connections.ssh.ark_ssh_connection import SSH_PORT
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionDetails, ArkConnectionResult


class ArkPTYSSHConnection(ArkConnection):
    __ANSI_STRIPPER: Any = re.compile(r'\x1b[^m]*m|\x1b\[\?2004[hl]')

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
        # pylint: disable=import-error
        from pexpect import pxssh

        if self.__is_connected:
            return
        try:
            target_port = SSH_PORT
            user = None
            if connection_details.port:
                target_port = connection_details.port
            credentials_map = {}
            if connection_details.credentials:
                user = connection_details.credentials.user
                if connection_details.credentials.password:
                    credentials_map['password'] = connection_details.credentials.password.get_secret_value()
                elif connection_details.credentials.private_key_filepath:
                    path = Path(connection_details.credentials.private_key_filepath)
                    if not path.exists():
                        raise ArkException(f'Given private key path [{path}] does not exist')
                    credentials_map['ssh_key'] = connection_details.credentials.private_key_filepath
            self.__ssh_client = pxssh.pxssh()
            self.__ssh_client.login(
                server=connection_details.address,
                username=user,
                port=target_port,
                login_timeout=30,
                **credentials_map,
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
        self.__ssh_client.logout()
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
        self.__ssh_client.sendline(command.command)
        self.__ssh_client.prompt()
        stdout = self.__ssh_client.before.decode()
        self.__ssh_client.sendline('echo $?')
        self.__ssh_client.prompt()
        exit_code_output = self.__ssh_client.before.decode()
        exit_code_output = ArkPTYSSHConnection.__ANSI_STRIPPER.sub('', exit_code_output)
        rc = int(exit_code_output.strip().splitlines()[-1])
        if rc != command.expected_rc and command.raise_on_error:
            raise ArkException(f'Failed to execute command [{command.command}] - [{rc}] - [{stdout}]')
        self._logger.debug(f'Command rc: [{rc}]')
        self._logger.debug(f'Command stdout: [{stdout}]')
        return ArkConnectionResult(stdout=stdout, rc=rc)
