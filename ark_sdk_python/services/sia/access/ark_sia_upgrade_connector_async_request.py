import time
from datetime import datetime
from http import HTTPStatus
from typing import Callable, Final, cast

from overrides import overrides
from requests import Response

from ark_sdk_python.common.ark_async_request import ArkAsyncRequest
from ark_sdk_python.common.ark_client import ArkClient
from ark_sdk_python.models.common import ArkAsyncRequestSettings, ArkAsyncStatus, ArkAsyncTask, ArkStatus
from ark_sdk_python.models.services.sia.access import ArkSIAConnector, ArkSIAConnectorModeCodes, ArkSIAUpgradeConnectorAsyncTask

GET_CONNECTOR_API: Final[str] = 'api/connectors/{connector_id}'


class ArkSIAUpgradeConnectorAsyncRequest(ArkAsyncRequest):
    def __init__(self, client: ArkClient, async_task: ArkAsyncTask, async_request_settings: ArkAsyncRequestSettings):
        super().__init__(client, async_task, async_request_settings)
        self.__is_exception_failure = False
        self.__is_timeout_failure = False

    @overrides
    def is_finished(self) -> bool:
        """
        Checks if the connector state has changed to available and upgrade is done
        If the connector is not found or any issue occurred, the task is finished with a failure

        Returns:
            bool: _description_
        """
        try:
            upgrade_async_task = cast(ArkSIAUpgradeConnectorAsyncTask, self._async_task)
            resp: Response = self._client.get(GET_CONNECTOR_API.format(connector_id=upgrade_async_task.connector.connector_id))
            if resp.status_code == HTTPStatus.OK:
                upgrade_async_task.connector = ArkSIAConnector.model_validate(resp.json())
                return upgrade_async_task.connector.is_latest_version or (
                    upgrade_async_task.connector.connector_mode != ArkSIAConnectorModeCodes.JOB_IN_PROGRESS
                    and upgrade_async_task.connector.last_job_status
                    in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'REJECTED', 'REMOVED', 'CANCELED']
                )
            elif resp.status_code == HTTPStatus.UNAUTHORIZED:
                if self._async_request_settings.poll_allow_refreshable_connection and self.client.refresh_connection_callback:
                    try:
                        self.client.refresh_connection_callback(self.client)
                        return self.is_finished()
                    except Exception as ex_refresh:
                        self._async_task.task_error = str(ex_refresh)
                        self.__is_exception_failure = True
                        self.__is_timeout_failure = True
                        return True
                else:
                    self.__is_timeout_failure = True
                    return True
            upgrade_async_task.connector.connector_mode = ArkSIAConnectorModeCodes.SUSPENDED
            upgrade_async_task.connector.last_job_status = 'FAILED'
            return True
        except Exception as ex:
            self._async_task.task_error = str(ex)
            self.__is_exception_failure = True
            return True

    @overrides
    def task_failed(self) -> bool:
        """
        Checks whether the connector upgrade has failed or not

        Returns:
            bool: _description_
        """
        return (
            self.is_finished()
            and self._async_task.task_status() == ArkStatus.Failed
            or self.__is_exception_failure
            or self.__is_timeout_failure
        )

    @overrides
    def task_timeout(self) -> bool:
        """
        Checks whether the sia upgrade task credentials were timed out

        Returns:
            bool: _description_
        """
        return self.__is_timeout_failure

    @overrides
    def poll(self, timeout_seconds: int, progress_callback: Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]) -> bool:
        """
        Polls until the connector is either done upgrading or failed in doing so

        Args:
            timeout_seconds (int): _description_
            progress_callback (Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]): _description_

        Returns:
            bool: _description_
        """
        start: datetime = datetime.now()
        progress_tick: int = 0
        current_status: ArkStatus = self._async_task.task_status()
        progress_time = timeout_seconds
        if progress_callback:
            progress_callback(self._async_task, progress_time, ArkAsyncStatus.StartedPolling)
        while not self.is_finished():
            self._logger.debug(f'Polling async task [{self._async_task.task_id}], current status: [{self._async_task.task_status()}]')
            now = datetime.now()
            delta = (now - start).seconds
            progress_time = timeout_seconds - delta
            if progress_time <= 0:
                break
            if current_status != self._async_task.task_status():
                current_status = self._async_task.task_status()
                if progress_callback:
                    progress_callback(self._async_task, progress_time, ArkAsyncStatus.StillPolling)
            elif progress_tick >= self._async_request_settings.progress_tick_count:
                progress_tick = 0
                if progress_callback:
                    progress_callback(self._async_task, progress_time, ArkAsyncStatus.StillPolling)
            progress_tick = progress_tick + 1
            time.sleep(self._async_request_settings.poll_sleep_time)
        if self.is_finished():
            if progress_callback:
                if self._async_task.task_status() == ArkStatus.Success:
                    progress_callback(self._async_task, progress_time, ArkAsyncStatus.Successful)
                    return True
                else:
                    progress_callback(self._async_task, progress_time, ArkAsyncStatus.Failed)
                    return False
        if progress_callback:
            if self.__is_timeout_failure:
                progress_callback(self._async_task, progress_time, ArkAsyncStatus.Timeout)
            else:
                progress_callback(self._async_task, progress_time, ArkAsyncStatus.Failed)
        return False
