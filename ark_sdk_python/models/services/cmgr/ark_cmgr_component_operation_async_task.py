from overrides import overrides
from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.common import ArkAsyncTask, ArkStatus
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponent, ArkCmgrComponentStatusCode, MaintenanceOperationStatus


class ArkCmgrComponentOperationAsyncTask(ArkAsyncTask):
    component: ArkCmgrComponent = Field(description="Component being operated on")
    operation: Literal["INSTALL", "UPGRADE", "REINSTALL", "UNINSTALL"] = Field(description="Operation being made")
    component_deleted: bool = Field(
        default=False,
        description="Whether the component was confirmed deleted after uninstall",
    )

    # pylint: disable=no-member
    @overrides
    def task_status(self) -> ArkStatus:
        if self.operation == "UNINSTALL" and self.component_deleted:
            return ArkStatus.Success
        if self.component.maintenance_operation_details.status == MaintenanceOperationStatus.SUCCEEDED:
            # For uninstall, keep polling after SUCCEEDED until the component is confirmed deleted (404)
            if self.operation == "UNINSTALL":
                return ArkStatus.InProgress
            if self.component.component_status == ArkCmgrComponentStatusCode.ACTIVE:
                return ArkStatus.Success
            return ArkStatus.Failed
        if self.component.maintenance_operation_details.status == MaintenanceOperationStatus.FAILED:
            return ArkStatus.Failed
        return ArkStatus.InProgress
