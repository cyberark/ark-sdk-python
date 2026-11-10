from typing import Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common import ArkOsType


class ArkSIAInstallRelay(ArkModel):
    https_relay_os: ArkOsType = Field(description='The type of the operating system for the HTTPS relay to be installed on')
    protocol_port_map: Dict[str, int] = Field(description='Map between protocol and port for the HTTPS relay')
    expiration_minutes: Optional[int] = Field(
        default=15,
        ge=15,
        le=240,
        description='The number of minutes the setup script will be valid for (15-240)',
    )
    proxy_host: Optional[str] = Field(default=None, description='Proxy host address for the HTTPS relay')
    proxy_port: Optional[int] = Field(default=443, description='Proxy port for the HTTPS relay')
    windows_installation_path: Optional[str] = Field(
        default=None,
        description='Custom installation path for the HTTPS relay on Windows machines',
    )
    target_machine: str = Field(description='Target machine on which to install the HTTPS relay on')
    username: str = Field(description='Username to connect with to the target machine')
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
