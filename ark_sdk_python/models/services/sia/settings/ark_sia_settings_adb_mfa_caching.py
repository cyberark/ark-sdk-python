from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsADBMfaCaching(ArkCamelizedModel):
    is_mfa_caching_enabled: Optional[bool] = Field(default=None, description="Is MFA caching is enabled")
    key_expiration_time_sec: Optional[int] = Field(default=None, description="The expiration time for the MFA caching key in seconds")
    client_ip_enforced: Optional[bool] = Field(default=None, description="Is client IP is enforced for MFA caching")
    token_usage_count: Optional[int] = Field(default=None, description="The number of times an MFA token can be used")
