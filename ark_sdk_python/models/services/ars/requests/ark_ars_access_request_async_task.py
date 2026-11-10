from typing import List

from overrides import overrides
from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.common import ArkStatus
from ark_sdk_python.models.common.ark_async_task import ArkAsyncTask
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request import (
    ArkARSAccessRequest,
    ArkARSAccessRequestResult,
    ArkARSAccessRequestState,
)


class ArkARSAccessRequestAsyncTask(ArkAsyncTask):
    request: ArkARSAccessRequest = Field(description='Request itself')
    action: Literal['StartRequest', 'UpdateRequest', 'FinalizeRequest', 'CancelRequest'] = Field(description='Action performed')
    target_statuses: List[ArkStatus] = Field(description='Target status')

    # pylint: disable=no-member
    @overrides
    def task_status(self) -> ArkStatus:
        if self.request.request_state == ArkARSAccessRequestState.FINISHED:
            if self.request.request_result in (
                ArkARSAccessRequestResult.APPROVED,
                ArkARSAccessRequestResult.FULFILLED,
                ArkARSAccessRequestResult.REJECTED,
                ArkARSAccessRequestResult.CANCELED,
            ):
                return ArkStatus.Success
            return ArkStatus.Failed
        if self.request.request_state == ArkARSAccessRequestState.EXPIRED:
            return ArkStatus.Failed
        if self.request.request_state == ArkARSAccessRequestState.PENDING:
            return ArkStatus.Pending
        if self.request.request_state in (
            ArkARSAccessRequestState.RUNNING,
            ArkARSAccessRequestState.FULFILLING,
            ArkARSAccessRequestState.REVERTING_FULFILLMENT,
            ArkARSAccessRequestState.STARTING,
        ):
            return ArkStatus.InProgress
        return ArkStatus.Failed
