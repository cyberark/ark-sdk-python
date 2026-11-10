from typing import Optional

from pydantic import Field, NonNegativeInt

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.access.ark_sia_https_relay_status_codes import ArkSIAHttpsRelayStatusCodes


class ArkSIAHttpsRelay(ArkCamelizedModel):
    id: str = Field(min_length=2, description='The HTTPS relay ID')
    host_ip: Optional[str] = Field(default=None, description='The host machine.')
    host_name: Optional[str] = Field(default=None, description='The host name.')
    version: Optional[str] = Field(default=None, description='The https relay version')
    active_sessions_count: NonNegativeInt = Field(default=0, description='How many active sessions currently running on this https relay.')
    status_code: ArkSIAHttpsRelayStatusCodes = Field(
        default=ArkSIAHttpsRelayStatusCodes.INACTIVE,
        description='The status of the https relay. 0 - The https relay is inactive and not communicating with the service, '
        '1 - The https relay is active, 2 - The https relay is inactive and blocked and cannot support any sessions'
        ' (this https relay should be deleted from SIA and the host machine).',
    )
    status: str = Field(default='INACTIVE', description='The human-readable status of the HTTPS relay')
    os: Optional[str] = Field(default=None, description='The operating system of the https relay host.')
    proxy_settings: Optional[str] = Field(default=None, description='The HTTP Proxy details if configured.')
    is_latest_version: bool = Field(default=True, description='Whether the https relay is updated with the latest version.')
    version_to_upgrade: Optional[str] = Field(default=None, description='The version to upgrade to if the https relay is not updated.')
    is_upgradable: bool = Field(description='Whether the https relay can be upgraded to the latest version.')
    last_job_status: Optional[str] = Field(default=None, description='The status of the last job executed on the https relay, if exists.')
    last_job_error_code: Optional[str] = Field(
        default=None, description='The error code of the last job executed on the https relay, if exists.'
    )
    last_job_status_description: Optional[str] = Field(
        default=None, description='The description of the last job executed on the https relay, if exists.'
    )
    last_job_info_update_date: Optional[str] = Field(description='The last time the last job status was updated, if exists.', default=None)
