from abc import ABC, abstractmethod
from typing import Callable

from ark_sdk_python.common.ark_client import ArkClient
from ark_sdk_python.common.ark_logger import get_logger
from ark_sdk_python.models.common import ArkAsyncRequestSettings, ArkAsyncStatus, ArkAsyncTask


class ArkAsyncRequest(ABC):
    def __init__(self, client: ArkClient, async_task: ArkAsyncTask, async_request_settings: ArkAsyncRequestSettings):
        self._async_task = async_task
        self._client = client
        self._async_request_settings = async_request_settings
        self._logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def is_finished(self) -> bool:
        """
        Checks whether or not the current async request has finished.

        Returns:
            bool: _description_
        """

    @abstractmethod
    def task_failed(self) -> bool:
        """
        Checks whether or the current async request failed.

        Returns:
            bool: _description_
        """

    @abstractmethod
    def task_timeout(self) -> bool:
        """
        Checks whether or not the current async request has timed out.

        Returns:
            bool: _description_
        """

    @abstractmethod
    def poll(self, timeout_seconds: int, progress_callback: Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]) -> bool:
        """
        Polls the async request until it has completed.
        Progress callbacks can also be used to return the async request's status.

        Args:
            timeout_seconds (int): _description_
            progress_callback (Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]): _description_

        Returns:
            bool: _description_
        """

    @property
    def async_task(self) -> ArkAsyncTask:
        return self._async_task

    @property
    def client(self) -> ArkClient:
        return self._client
