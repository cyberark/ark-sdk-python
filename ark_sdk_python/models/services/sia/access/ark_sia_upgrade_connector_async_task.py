from overrides import overrides
from pydantic import Field

from ark_sdk_python.models.common import ArkAsyncTask, ArkStatus
from ark_sdk_python.models.services.sia.access.ark_sia_connector import ArkSIAConnector, ArkSIAConnectorModeCodes


class ArkSIAUpgradeConnectorAsyncTask(ArkAsyncTask):
    connector: ArkSIAConnector = Field(description='Connector being upgraded')

    # pylint: disable=no-member
    @overrides
    def task_status(self) -> ArkStatus:
        if self.connector.is_latest_version:
            return ArkStatus.Success
        if self.connector.connector_mode == ArkSIAConnectorModeCodes.JOB_IN_PROGRESS or (
            self.connector.last_job_status and self.connector.last_job_status == 'IN_PROGRESS'
        ):
            return ArkStatus.InProgress
        elif self.connector.last_job_status and self.connector.last_job_status in [
            'FAILED',
            'TIMED_OUT',
            'REJECTED',
            'CANCELED',
            'REMOVED',
        ]:
            return ArkStatus.Failed
        elif self.connector.connector_mode == ArkSIAConnectorModeCodes.AVAILABLE or (
            self.connector.last_job_status and self.connector.last_job_status == 'SUCCEEDED'
        ):
            return ArkStatus.Success
        return ArkStatus.Failed
