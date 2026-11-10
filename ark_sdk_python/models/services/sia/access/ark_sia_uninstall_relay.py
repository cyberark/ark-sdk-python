from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common.ark_os_type import ArkOsType


class ArkSIAUninstallRelay(ArkModel):
    https_relay_os: ArkOsType = Field(description='The type of the operating system the HTTPS relay is installed on')
    https_relay_id: str = Field(description='HTTPS relay id to get information for uninstallation')
    username: str = Field(description='Username to connect with to the target machine')
    target_machine: Optional[str] = Field(
        default=None,
        description='Target machine on which to uninstall the HTTPS relay from, if not given, uses the host_ip from the relay information',
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
