from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common.ark_os_type import ArkOsType


class ArkSIADeleteHttpsRelay(ArkModel):
    https_relay_id: str = Field(description='Https relay id we would like to delete')
    force_delete: Optional[bool] = Field(
        default=None, description='When true, forces deletion of the HTTPS relay even if it has active sessions'
    )
    uninstall_relay: Optional[bool] = Field(
        description='Whether to try and uninstall the HTTPS relay from the target machine as well', default=False
    )
    https_relay_os: Optional[ArkOsType] = Field(
        default=None, description='OS type of the target machine, required when uninstall_relay is True'
    )
    username: Optional[str] = Field(default=None, description='Username to connect with to the target machine')
    target_machine: Optional[str] = Field(
        default=None,
        description='Target machine on which to uninstall the relay from, if not given, uses the host_ip from the relay information',
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
