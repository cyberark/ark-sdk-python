from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsHttpsRelay(ArkCamelizedModel):
    is_https_relay_enabled: Optional[bool] = Field(default=None, description='Whether the HTTPS Relay feature is enabled')
    relay_host: Optional[str] = Field(default=None, description='The HTTPS Relay host address (IP or FQDN)')
    ssh_relay_port: Optional[int] = Field(default=None, description='The SSH port used by the HTTPS Relay')
