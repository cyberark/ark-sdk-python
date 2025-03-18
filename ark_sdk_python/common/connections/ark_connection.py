from abc import ABC, abstractmethod

from ark_sdk_python.common.ark_logger import get_logger
from ark_sdk_python.models.common.connections import ArkConnectionCommand, ArkConnectionDetails, ArkConnectionResult


class ArkConnection(ABC):
    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def connect(self, connection_details: ArkConnectionDetails) -> None:
        """
        Connects to the target with given information

        Args:
            connection_details (ArkConnectionDetails): _description_
        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects the active session
        """

    @abstractmethod
    def suspend_connection(self) -> None:
        """
        Suspends the session from command execution
        """

    @abstractmethod
    def restore_connection(self) -> None:
        """
        Restores the session
        """

    @abstractmethod
    def is_suspended(self) -> bool:
        """
        Checks whether session is suspended

        Returns:
            bool: _description_
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Checks whether session is connected

        Returns:
            bool: _description_
        """

    @abstractmethod
    def run_command(self, command: ArkConnectionCommand) -> ArkConnectionResult:
        """
        Runs a remote connection command

        Args:
            command (ArkConnectionCommand): _description_

        Returns:
            ArkConnectionResult: _description_
        """
