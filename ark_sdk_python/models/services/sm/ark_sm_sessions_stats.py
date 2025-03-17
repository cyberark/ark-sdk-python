from typing import Dict

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkApplicationCode, ArkProtocolType, ArkWorkspaceType
from ark_sdk_python.models.services.sm.ark_sm_session import ArkSMSessionStatus


class ArkSMSessionsStats(ArkModel):
    sessions_count: int = Field(description='Sessions count in the last 30 days')
    sessions_count_per_application_code: Dict[ArkApplicationCode, int] = Field(description='Sessions count per application code')
    sessions_count_per_platform: Dict[ArkWorkspaceType, int] = Field(description='Sessions count per platform')
    sessions_count_per_status: Dict[ArkSMSessionStatus, int] = Field(description='Sessions count per status')
    sessions_count_per_protocol: Dict[ArkProtocolType, int] = Field(description='Sessions count per protocol')
    sessions_failure_count: int = Field(description='Sessions count with failures')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('sessions_count_per_platform', mode="before")
    @classmethod
    def validate_sessions_count_per_platform(cls, val):
        if val is not None:
            new_val = {}
            for platform in val.keys():
                if ArkWorkspaceType(platform) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                    ArkWorkspaceType.UNKNOWN,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val[ArkWorkspaceType(platform)] = val[platform]
        return val

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('sessions_count_per_protocol', mode="before")
    @classmethod
    def validate_sessions_count_per_protocol(cls, val):
        if val is not None:
            new_val = {}
            for protocol in val.keys():
                if ArkProtocolType(protocol) not in [
                    ArkProtocolType.SSH,
                    ArkProtocolType.RDP,
                    ArkProtocolType.CLI,
                    ArkProtocolType.CONSOLE,
                    ArkProtocolType.HTTPS,
                    ArkProtocolType.K8S,
                    ArkProtocolType.DB,
                ]:
                    raise ValueError('Invalid Protocol Type')
                new_val[ArkProtocolType(protocol)] = val[protocol]
        return val
