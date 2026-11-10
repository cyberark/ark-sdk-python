from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponent, ArkCmgrComponentStatusCode


class ArkCmgrHost(ArkCamelizedModel):
    hostname: str = Field(description='Hostname of the host machine')
    private_ip: str = Field(description='Private ip of the host machine')
    public_ip: str = Field(description='Public ip of the host machine')
    os: ArkOsType = Field(description='OS of the host machine')
    os_version: str = Field(description='OS version of the host machine')
    os_name: str = Field(description='OS name of the host machine')
    cloud_region: Optional[str] = Field(default=None, description='If the host machine is in a cloud environment, its region')
    cloud_account: Optional[str] = Field(default=None, description='If the hostmachine is in a cloud environment, its account')
    cpu_type: str = Field(description='Type of the cpu of the host machine')
    total_cpu: int = Field(description='Total number of cpus of the host machine')
    used_cpu: float = Field(description='Used CPU percentage statistic of the host machine')
    total_memory: float = Field(description='Overall memory in GB of the host machine')
    used_memory: float = Field(description='Used memory in GB statistic of the host machine')


class ArkCmgrConnector(ArkCamelizedModel):
    connector_id: str = Field(description='ID of the connector')
    connector_status: ArkCmgrComponentStatusCode = Field(description='Current status of the connector')
    platform_type: ArkWorkspaceType = Field(description='Platform of the connector')
    connector_pool_id: Optional[str] = Field(default=None, description='The connector pool which the connector is part of')
    version: str = Field(description='Version of the connector')
    upgrade_versions: List[str] = Field(description='Possible upgrade versions of the connector', default_factory=list)
    installed_at: int = Field(description='When was the component installed at, as unix epoch timestamp')
    updated_at: int = Field(description='When was the component last updated, as unix epoch timestamp')
    host: ArkCmgrHost = Field(description='Connector host monitoring stats')
    components: List[ArkCmgrComponent] = Field(description='Components that are installed which the connector detected')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('platform_type', mode="before")
    @classmethod
    def validate_platform_type(cls, val):
        if val is not None:
            if ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.UNKNOWN,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val
