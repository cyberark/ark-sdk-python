from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrComponentStatusCode(str, Enum):
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    INITIALIZING = 'Initializing'
    UNKNOWN = 'Unknown'
    DISCONNECTED = 'Disconnected'
    NOT_FOUND = 'Not Found'
    DOWNLOADED = 'Downloaded'  # deprecated
    PENDING_INSTALLATION = 'PendingInstallation'  # deprecated
    INSTALLING = 'Installing'  # deprecated
    UPGRADING = 'Upgrading'  # deprecated
    ERROR = 'Error'  # deprecated
    SUSPENDED = 'Suspended'  # deprecated
    MAINTENANCE_FAILED = 'MaintenanceFailed'  # deprecated
    INSTALLATION_FAILED = 'InstallationFailed'  # deprecated


class ArkCmgrMaintenanceType(str, Enum):
    INSTALLATION = 'Installation'
    UPGRADE = 'Upgrade'
    UNINSTALLATION = 'Uninstallation'


class MaintenanceAdditionalInformation(ArkCamelizedModel):
    error: Optional[str] = Field(default=None, title='Error details for the job failure')
    is_retriable: Optional[bool] = Field(default=None, title='Indicates if the job is retriable')
    result_file_content: Optional[str] = Field(default=None, title='The content of the result file')


class ArkCmgrMaintenanceStatus(ArkCamelizedModel):
    maintenance_type: ArkCmgrMaintenanceType = Field(description='Type of maintenance')
    progress: float = Field(description='Current maintanance operation percentage')
    current_step: str = Field(description='Current maintenance operation step')
    additional_information: Optional[Dict[str, str]] = Field(default=None, description='Additional maintenance operation information')


class MaintenanceOperationStatus(str, Enum):
    """
    The list of lifecycle operation statuses.
    """

    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'


class MaintenanceOperationDetails(ArkCamelizedModel):
    """Lifecycle Operation Status Details"""

    type: Optional[ArkCmgrMaintenanceType] = Field(title='Maintenance operation type', examples=[ArkCmgrMaintenanceType.INSTALLATION])
    progress: float
    current_step: Optional[str] = Field(default=None, title='The current step', examples=['Hardening'])
    additional_information: Optional[MaintenanceAdditionalInformation] = Field(
        default=None, title='Additional information in case of a failure'
    )
    status: Optional[MaintenanceOperationStatus] = Field(default=None, title='The status of the lifecycle operation')


class ArkCmgrComponent(ArkCamelizedModel):
    component_id: str = Field(description='ID of the component')
    component_name: str = Field(description='Name of the component')
    acronym: Optional[str] = Field(default=None, description='Acronym of the component')
    component_status: ArkCmgrComponentStatusCode = Field(description='Current status of the component')
    connector_id: str = Field(description='Related connector id of the component')
    version: str = Field(description='Version of the component')
    upgrade_versions: List[str] = Field(description='Possible upgrade versions of the component', default_factory=list)
    used_cpu: float = Field(description='Used CPU percentage statistic of the component')
    used_memory: float = Field(description='Used memory in GB statistic of the component')
    installed_at: int = Field(description='When was the component installed at, as unix epoch timestamp')
    updated_at: int = Field(description='When was the component last updated, as unix epoch timestamp')
    maintenance_operation_details: Optional[MaintenanceOperationDetails] = Field(
        default=None, title='The status of the current maintenance operation'
    )
