from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsSSHMfaCaching(ArkCamelizedModel):
    is_mfa_caching_enabled: Optional[bool] = Field(default=None, description="Is MFA caching is enabled.")
    key_expiration_time_sec: Optional[int] = Field(default=None, description="Expiration time for the MFA caching key in seconds.")
