from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsStandingAccess(ArkCamelizedModel):
    standing_access_available: Optional[bool] = Field(default=None, description="Whether standing access is available")
    session_max_duration: Optional[int] = Field(default=None, description="Maximum duration of a session")
    session_idle_time: Optional[int] = Field(default=None, description="Idle time before a session is considered inactive")
    fingerprint_validation: Optional[bool] = Field(default=None, description="Whether fingerprint validation is enabled")
    ssh_standing_access_available: Optional[bool] = Field(default=None, description="Whether SSH standing access is available")
    rdp_standing_access_available: Optional[bool] = Field(default=None, description="Whether RDP standing access is available")
    adb_standing_access_available: Optional[bool] = Field(default=None, description="Whether ADB standing access is available")
