from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr


class ArkSIADeleteConnector(ArkModel):
    connector_id: str = Field(description='The id of the connector to delete')
    force_delete: Optional[bool] = Field(default=None, description='When true, forces deletion of the connector even if it is active')
    uninstall_connector: Optional[bool] = Field(
        description='Whether to try and uninstall the connector from the target machine as well', default=False
    )
    username: Optional[str] = Field(default=None, description='Username to connect with to the target machine')
    target_machine: Optional[str] = Field(
        default=None,
        description='Target machine on which to uninstall the connector from, if not given, uses the connector_host_ip from the connector information',
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
