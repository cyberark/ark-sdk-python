from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkApplicationCode


class ArkSMSessionActivity(ArkCamelizedModel):
    uuid: str = Field(description='ID of the audit')
    tenant_id: str = Field(description='Tenant id of the audit')
    timestamp: datetime = Field(description='Time of the audit')
    username: str = Field(description='Username of the audit')
    application_code: ArkApplicationCode = Field(description='Application code of the audit')
    action: str = Field(description='Action performed for the audit')
    user_id: str = Field(description='Id of the user who performed the audit')
    source: str = Field(description='Source of the audit')
    action_type: str = Field(description='Type of action for the audit')
    audit_code: Optional[str] = Field(description='Audit code of the audit')
    command: Optional[str] = Field(description='Command performed as part of the audit')
    target: Optional[str] = Field(description='Target of the audit')
    service_name: Optional[str] = Field(description='Service name of the audit')
    session_id: Optional[str] = Field(description='Session id of the audit if related to a session')
    message: Optional[str] = Field(description='Message of the audit')


class ArkSMSessionActivities(ArkCamelizedModel):
    activities: List[ArkSMSessionActivity] = Field(description='List of the session activities')
    filtered_count: int = Field(description='How many session activities were filtered')
    returned_count: int = Field(description='How many session activities were returned')
