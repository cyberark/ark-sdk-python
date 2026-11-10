from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel, ArkModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType


class ArkSIAConnectorStatusCodes(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    DOWNLOADED = 2


class ArkSIAExtendedConnectorStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2
    PREPARING_FOR_MAINTENANCE = 3
    READY_FOR_MAINTENANCE = 4


class ArkSIAConnectorModeCodes(IntEnum):
    AVAILABLE = 0
    JOB_IN_PROGRESS = 1
    SUSPENDED = 2


class Status(str, Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    WARNING = 'Warning'
    SUSPENDED = 'Suspended'


class ArkSIAConnectorHealth(ArkCamelizedModel):
    id: str = Field(min_length=2, description='The connector Id')
    workspace_id: Optional[str] = Field(
        description='The workspace ID where the connector host is in, '
        'relevant only for the following connector_host_type: AWS (the AWS Account ID) and AZURE (the subscription ID).',
        default=None,
    )
    host_instance_id: Optional[str] = Field(
        description='The host ID. For AWS this is the Instance ID, for Azure this is the VM resource ID', default=None
    )
    region: Optional[str] = Field(description='The region where the connector host is in.', default=None)
    host_ip: Optional[str] = Field(description='The host machine.', default=None)
    host_name: Optional[str] = Field(description='The host name.', default=None)
    host_type: Optional[str] = Field(
        description='The platform type where the host is in. Valid values: AWS, AZURE or ON-PREMISE.', default=None
    )
    host_network: Optional[str] = Field(
        description='The virtual network where the host is in. For AWS this is the  VPC, for AZURE this is the Vnet.', default=None
    )
    host_subnet: Optional[str] = Field(description='The subnet where the host is in.', default=None)
    version: Optional[str] = Field(description='The connector version', default=None)
    active_sessions_count: int = Field(description='How many active sessions currently running on this connector.', ge=0)
    status: str = Field(description='The current connector status', default=Status.INACTIVE.value)
    os: Optional[str] = Field(description='The operating system of the connector host.', default=None)
    proxy_settings: Optional[str] = Field(description='The HTTP Proxy details if configured.', default=None)
    is_latest_version: bool = Field(description='Whether the connector is updated with the latest version.')


class ArkSIAConnector(ArkModel):
    tenant_id: Optional[str] = Field(description='The tenant where the connector resides on', default=None)
    connector_id: str = Field(description='The connector id')
    account: Optional[str] = Field(default=None, description='The account which the connector resides on', alias='aws_account')
    host_instance_id: Optional[str] = Field(
        default=None, description='The instance identifier which the connector resides in', alias='aws_host_instance_id'
    )
    region: Optional[str] = Field(default=None, description='The region which the connector resides in', alias='aws_region')
    connector_host_ip: str = Field(description='The ip of the connector machine')
    connector_host_name: str = Field(description='The hostname of the connector machine')
    connector_host_type: ArkWorkspaceType = Field(description='The host type of the connector machine')
    connector_host_os_version: Optional[str] = Field(default=None, description='OS version of the machine which the connector resides in')
    connector_host_outbound_ip: Optional[str] = Field(default=None, description='Outbound ip of the connector host machine')
    connector_host_vpc: Optional[str] = Field(default=None, description='The connector vpc network which the connector resides in')
    connector_host_subnet: Optional[str] = Field(
        default=None, description='The connector subnet within the vpc which the connector resides in'
    )
    connector_host_subnet_cidr: Optional[str] = Field(default=None, description='The connector cidr of the subnet')
    connector_version: str = Field(description='Version of the connector')
    total_memory: Optional[int] = Field(default=None, description='Total memory metric of the connector')
    cpu_count: Optional[int] = Field(default=None, description='CPU count metric of the connector')
    cpu_type: Optional[str] = Field(default=None, description='CPU type metric of the connector')
    created_time: Optional[datetime] = Field(default=None, description='When the connector was created')
    active_sessions_count: int = Field(description='Current active sessions count on the connector')
    update_time: Optional[datetime] = Field(default=None, description='Last update time of the connector')
    status_code: ArkSIAExtendedConnectorStatus = Field(description='Current status of the connector')
    connector_build_date: Optional[str] = Field(default=None, description='Build date of the connector binaries')
    connector_os: ArkOsType = Field(description='OS type of which the connector resides in')
    sha512_checksum: Optional[str] = Field(default=None, description='Sha signaute of the connector binaries')
    connector_mode: Optional[ArkSIAConnectorModeCodes] = Field(default=None, description='Current connector mode')
    last_job_info_update_date: Optional[str] = Field(default=None, description='Connector last job update date')
    last_job_status: Optional[str] = Field(default=None, description='Connector job status')
    last_job_error_code: Optional[str] = Field(default=None, description='Connector job error code')
    last_job_status_description: Optional[str] = Field(default=None, description='Connector job status description')
    proxy_settings: Optional[str] = Field(default=None, description='Info about proxy settings of the connector if exists')
    is_upgradable: Optional[bool] = Field(default=None, description='Whether the connector is upgradable and not at latest version')
    is_latest_version: bool = Field(description='Whether the connector is at the latest version and not upgradable')
    maintenance: Optional[bool] = Field(default=None, description='Whether the connector is in maintenance mode')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connector_host_type', mode="before")
    @classmethod
    def validate_connector_host_type(cls, val):
        if val is not None:
            if ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.FAULT,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val
