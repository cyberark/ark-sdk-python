import os
import re
import subprocess
import threading
import time
from shutil import which
from typing import Any, Final, Optional

from overrides import overrides

from ark_sdk_python.common.connections.ark_connection import ArkConnection
from ark_sdk_python.common.connections.ssh.ark_ssh_connection import SSH_PORT
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionDetails, ArkConnectionResult


class ArkPTYSSHWinConnection(ArkConnection):
    __ANSI_COLOR_STRIPPER: Final[Any] = re.compile(r'\x1b[^m]*m|\x1b\[\?2004[hl]')
    __ANSI_ESCAPE_STRIPPER: Final[Any] = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    __PROMPT_REGEX: Final[Any] = re.compile(r"[#$]")
    __PASSWORD_PROMPT_REGEX: Final[Any] = re.compile(
        r"(?i)(?:password:)|(?:passphrase for key)|(?:^Please enter your password[\s\S]+.+ >:$)"
    )
    __EXIT_MAKRER: Final[str] = '__ARK_RC_MARK__'
    __DEFAULT_COL_SIZE: Final[int] = 80
    __DEFAULT_ROW_SIZE: Final[int] = 24
    __DEFAULT_NONEAGER_TIMEOEUT: Final[float] = 1.0
    __DEFAULT_PROMPT_OVERALL_TIMEOUT: Final[float] = 20.0
    __CHAR_SLEEP_TIME: Final[float] = 0.05

    def __init__(self):
        super().__init__()
        self.__is_connected: bool = False
        self.__is_suspended: bool = False
        self.__pty: Optional[Any] = None
        self.__output_lock: threading.Lock = threading.Lock()
        self.__buffer: str = ''

    def __strip_ansi(self, ansi_input: str) -> str:
        ansi_input = ansi_input.strip()
        ansi_input = ArkPTYSSHWinConnection.__ANSI_COLOR_STRIPPER.sub('', ansi_input)
        ansi_input = ArkPTYSSHWinConnection.__ANSI_ESCAPE_STRIPPER.sub('', ansi_input)
        return ansi_input

    def __reset_buffer(self) -> None:
        with self.__output_lock:
            self.__buffer = ''

    def __read_until_latest_prompt(
        self,
        password: Optional[str] = None,
        noneager_timeout: float = __DEFAULT_NONEAGER_TIMEOEUT,
        overall_timeout: float = __DEFAULT_PROMPT_OVERALL_TIMEOUT,
        login_prompt: bool = False,
        expected_prompt: Any = __PROMPT_REGEX,
    ) -> None:
        buffer = ''
        prompt_found_at = -1
        start_time = time.time()
        noneager_start_time = start_time

        while True:
            char = self.__pty.read(1)
            if not char:
                if ArkPTYSSHWinConnection.__PASSWORD_PROMPT_REGEX.search(self.__strip_ansi(buffer)) and not password and login_prompt:
                    raise RuntimeError(f'Password prompt with no password given [{buffer}]')
                if (time.time() - noneager_start_time > noneager_timeout) and prompt_found_at != -1:
                    break
                if (time.time() - start_time) > overall_timeout and prompt_found_at == -1:
                    raise RuntimeError(f'Timeout while waiting for prompt [{buffer}]')
                time.sleep(ArkPTYSSHWinConnection.__CHAR_SLEEP_TIME)
                continue

            buffer += char

            with self.__output_lock:
                self.__buffer += char

            if ArkPTYSSHWinConnection.__PASSWORD_PROMPT_REGEX.search(self.__strip_ansi(buffer)) and login_prompt:
                if not password:
                    raise RuntimeError(f'Password prompt with no password given [{buffer}]')
                self.__pty.write(password + '\n')
                buffer = ""
                prompt_found_at = -1
                continue

            if expected_prompt.search(buffer):
                prompt_found_at = len(buffer)

            noneager_start_time = time.time()

        if prompt_found_at != -1:
            with self.__output_lock:
                self.__buffer = buffer

    @overrides
    def connect(self, connection_details: ArkConnectionDetails) -> None:
        """
        Performs SSH connection with given details or keys
        Saves the ssh session to be used for command executions
        Done using windows pty

        Args:
            connection_details (ArkConnectionDetails): _description_

        Raises:
            ArkException: _description_
        """
        # pylint: disable=import-error
        import winpty

        if self.__is_connected:
            return

        address = connection_details.address
        user = connection_details.credentials.user
        port = connection_details.port or SSH_PORT
        password = None
        key_path = None
        if connection_details.credentials.password:
            password = connection_details.credentials.password.get_secret_value()
        elif connection_details.credentials.private_key_filepath:
            key_path = connection_details.credentials.private_key_filepath

        ssh_args = [f'{user}@{address}', '-p', str(port), '-o', 'StrictHostKeyChecking=no']
        if key_path:
            ssh_args.extend(['-i', str(key_path)])
        try:
            self.__pty = winpty.PTY(
                cols=ArkPTYSSHWinConnection.__DEFAULT_COL_SIZE,
                rows=ArkPTYSSHWinConnection.__DEFAULT_ROW_SIZE,
                backend=winpty.enums.Backend.WinPTY,
            )
            ssh_full_cmd = which('ssh', path=os.environ.get('PATH', os.defpath))
            self.__pty.spawn(ssh_full_cmd, cmdline=' ' + subprocess.list2cmdline(ssh_args))
            self.__read_until_latest_prompt(password, login_prompt=True)
            self.__is_connected = True
        except Exception as ex:
            raise ArkException(f'Failed to ssh connect [{str(ex)}]') from ex

    @overrides
    def disconnect(self) -> None:
        """
        Disconnects the ssh session
        """
        if self.__pty:
            self.__pty.write('exit\n')
            self.__pty = None
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
        Runs a command over ssh session via pty, returning the result accordingly
        stderr is not supported, only stdout is returned, and it'll contain everything including stderr

        Args:
            command (ArkConnectionCommand): _description_

        Raises:
            ArkException: _description_

        Returns:
            ArkConnectionResult: _description_
        """
        if not self.__is_connected or self.__is_suspended:
            raise ArkException('Cannot run command while not connected or suspended')

        self._logger.debug(f'Running command [{command.command}]')

        self.__reset_buffer()
        self.__pty.write(command.command + "\n")
        self.__read_until_latest_prompt()

        with self.__output_lock:
            stdout = self.__buffer.strip()

        self.__reset_buffer()
        self.__pty.write(f'echo {ArkPTYSSHWinConnection.__EXIT_MAKRER}_$?;\n')
        self.__read_until_latest_prompt()

        with self.__output_lock:
            lines = self.__buffer.strip().splitlines()

        rc = None
        for line in lines:
            line = self.__strip_ansi(line)
            if line.startswith(f'{ArkPTYSSHWinConnection.__EXIT_MAKRER}_'):
                try:
                    rc = int(line[len(ArkPTYSSHWinConnection.__EXIT_MAKRER) + 1 :])  # +1 for the underscore
                    break
                except ValueError:
                    continue
        if rc is None:
            raise ArkException(f"Failed to parse exit code from output - [{self.__buffer}]")
        if rc != command.expected_rc and command.raise_on_error:
            raise ArkException(f'Failed to execute command [{command.command}] - [{rc}] - [{stdout}]')
        self._logger.debug(f'Command rc: [{rc}]')
        self._logger.debug(f'Command stdout: [{stdout}]')
        return ArkConnectionResult(stdout=stdout, rc=rc)
