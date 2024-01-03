from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkAccessMethod, ArkApplicationCode, ArkProtocolType, ArkWorkspaceType


class ArkSMSessionStatus(str, Enum):
    ACTIVE = 'Active'
    ENDED = 'Ended'
    FAILED = 'Failed'


class ArkSMSession(ArkCamelizedModel):
    tenant_id: Optional[str] = Field(description='Tenant id of the session')
    session_id: str = Field(description='Session id')
    session_status: Optional[ArkSMSessionStatus] = Field(description='Status of the session')
    session_duration: Optional[timedelta] = Field(description='Duration of the session in seconds')
    end_reason: Optional[str] = Field(description='End reason for the session')
    error_code: Optional[str] = Field(description='Error code for the session')
    application_code: Optional[ArkApplicationCode] = Field(description='Application code of the session')
    access_method: Optional[ArkAccessMethod] = Field(description='Access method of the session')
    start_time: Optional[datetime] = Field(description='Start time of the session')
    end_time: Optional[datetime] = Field(description='End time of the session')
    user: Optional[str] = Field(description='Username of the session')
    source: Optional[str] = Field(description='Source of the session (Usually Ip)')
    target: Optional[str] = Field(description='Target of the session (Usually Ip/Dns)')
    target_username: Optional[str] = Field(description='Target username of the session')
    protocol: Optional[ArkProtocolType] = Field(description='Connection protocol of the session')
    platform: Optional[ArkWorkspaceType] = Field(description='Connection platform of the session')
    custom_data: Optional[Dict[str, Any]] = Field(description='Custom data of the session')


class ArkSMSessions(ArkCamelizedModel):
    sessions: List[ArkSMSession] = Field(description='List of the sessions')
    filtered_count: int = Field(description='How many sessions were filtered')
    returned_count: int = Field(description='How many sessions were returned')
