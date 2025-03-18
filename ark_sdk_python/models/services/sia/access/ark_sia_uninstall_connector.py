from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common.ark_os_type import ArkOsType


class ArkSIAUninstallConnector(ArkModel):
    connector_os: ArkOsType = Field(description='The type of the operating system for the connector is installed on')
    connector_id: str = Field(description='Connector id to get information for uninstallation')
    username: str = Field(description='Username to connect with to the target machine')
    target_machine: str = Field(
        description='Target machine on which to uninstall the connector from, if not given, uses the connector_host_ip from the connector information',
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
