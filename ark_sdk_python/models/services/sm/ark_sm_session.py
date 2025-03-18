from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkAccessMethod, ArkApplicationCode, ArkProtocolType, ArkWorkspaceType


class ArkSMSessionStatus(str, Enum):
    ACTIVE = 'Active'
    ENDED = 'Ended'
    FAILED = 'Failed'


class ArkSMSession(ArkCamelizedModel):
    tenant_id: Optional[str] = Field(description='Tenant id of the session')
    session_id: str = Field(description='Session id')
    session_status: Optional[ArkSMSessionStatus] = Field(default=None, description='Status of the session')
    session_duration: Optional[timedelta] = Field(default=None, description='Duration of the session in seconds')
    end_reason: Optional[str] = Field(default=None, description='End reason for the session')
    error_code: Optional[str] = Field(default=None, description='Error code for the session')
    application_code: Optional[ArkApplicationCode] = Field(default=None, description='Application code of the session')
    access_method: Optional[ArkAccessMethod] = Field(default=None, description='Access method of the session')
    start_time: Optional[datetime] = Field(default=None, description='Start time of the session')
    end_time: Optional[datetime] = Field(default=None, description='End time of the session')
    user: Optional[str] = Field(default=None, description='Username of the session')
    source: Optional[str] = Field(default=None, description='Source of the session (Usually Ip)')
    target: Optional[str] = Field(default=None, description='Target of the session (Usually Ip/Dns)')
    target_username: Optional[str] = Field(default=None, description='Target username of the session')
    protocol: Optional[ArkProtocolType] = Field(default=None, description='Connection protocol of the session')
    platform: Optional[ArkWorkspaceType] = Field(default=None, description='Connection platform of the session')
    custom_data: Optional[Dict[str, Any]] = Field(default=None, description='Custom data of the session')
    is_recording: Optional[bool] = Field(default=None, description='Whether the session is recorded or not')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('platform', mode="before")
    @classmethod
    def validate_platform(cls, val):
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

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('protocol', mode="before")
    @classmethod
    def validate_protocol(cls, val):
        if val is not None:
            if ArkProtocolType(val) not in [
                ArkProtocolType.SSH,
                ArkProtocolType.RDP,
                ArkProtocolType.CLI,
                ArkProtocolType.CONSOLE,
                ArkProtocolType.HTTPS,
                ArkProtocolType.K8S,
                ArkProtocolType.DB,
            ]:
                raise ValueError('Invalid Protocol Type')
            return ArkProtocolType(val)
        return val


class ArkSMSessions(ArkCamelizedModel):
    sessions: List[ArkSMSession] = Field(description='List of the sessions')
    filtered_count: int = Field(description='How many sessions were filtered')
    returned_count: int = Field(description='How many sessions were returned')
