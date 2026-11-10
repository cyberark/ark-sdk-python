from typing import Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkOsType


class ArkSIAGetHttpsRelaySetupScript(ArkModel):
    https_relay_os: ArkOsType = Field(description='The type of the operating system for the HTTPS relay to be installed on')
    protocol_port_map: Dict[str, int] = Field(description='Map between protocol and port for the HTTPS relay')
    expiration_minutes: Optional[int] = Field(
        default=15, ge=15, le=240, description='Expiration time in minutes for the generated setup script, between 15 and 240 minutes'
    )
    proxy_host: Optional[str] = Field(default='', description='Optional proxy host to be configured for the HTTPS relay')
    proxy_port: Optional[int] = Field(default=443, description='Optional proxy port to be configured for the HTTPS relay')
    windows_installation_path: Optional[str] = Field(
        default='', description='Optional custom installation path for the HTTPS relay on Windows'
    )
