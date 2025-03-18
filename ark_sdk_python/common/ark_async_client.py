from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple, Type

from ark_sdk_python.common.ark_async_request import ArkAsyncRequest
from ark_sdk_python.common.ark_client import ArkClient
from ark_sdk_python.models.ark_model import ArkPollableModel
from ark_sdk_python.models.common import ArkAsyncRequestSettings
from ark_sdk_python.models.common.ark_async_task import ArkAsyncTask


class ArkAsyncClient(ABC, ArkClient):
    def __init__(
        self,
        async_request_settings: ArkAsyncRequestSettings = None,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        token_type: str = 'Bearer',
        cookies: Optional[List] = None,
        auth_header_name: str = 'Authorization',
        auth: Optional[Tuple[str, str]] = None,
        refresh_connection_callback: Optional[Callable[['ArkClient'], None]] = None,
        origin_verify: Optional[str] = None,
        origin_verify_header_name: str = 'x-origin-verify',
    ) -> None:
        super().__init__(
            base_url,
            token,
            token_type,
            cookies,
            auth_header_name,
            auth,
            refresh_connection_callback=refresh_connection_callback,
            origin_verify=origin_verify,
            origin_verify_header_name=origin_verify_header_name,
        )
        self.__async_request_settings = async_request_settings or ArkAsyncRequestSettings()

    @abstractmethod
    def async_request_for(self, poll_model: ArkPollableModel, async_task: ArkAsyncTask) -> ArkAsyncRequest:
        """
        Creates an async request for the specified model and task.
        The request polls for async operations as defined by the poll model's implementation.

        Args:
            poll_model (ArkPollableModel): _description_
            async_task (ArkAsyncTask): _description_

        Returns:
            ArkAsyncRequest: _description_
        """

    @staticmethod
    @abstractmethod
    def async_task_type() -> Type[ArkAsyncTask]:
        """
        Returns the client's async task type.

        Returns:
            Type[ArkAsyncTask]: _description_
        """

    @staticmethod
    @abstractmethod
    def async_request_type() -> Type[ArkAsyncRequest]:
        """
        Returns the client's async request type.

        Returns:
            Type[ArkAsyncTask]: _description_
        """

    @property
    def async_request_settings(self) -> ArkAsyncRequestSettings:
        return self.__async_request_settings
