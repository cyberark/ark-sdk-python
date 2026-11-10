from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common import ArkOsType
from ark_sdk_python.models.services.cmgr.ark_cmgr_get_connector_setup_script import ArkCmgrProxyDetails


class ArkCmgrInstallConnector(ArkModel):
    os_type: ArkOsType = Field(description='OS Type to generate the setup script for')
    version: Optional[str] = Field(
        default=None, description='The version of the connector to install, if not given, stable version will be installed'
    )
    installation_path: Optional[str] = Field(default=None, description='Where to install the connector on the machine')
    connector_pool_id: Optional[str] = Field(default=None, description='Connector pool id to associate the connector to')
    proxy_details: Optional[ArkCmgrProxyDetails] = Field(
        default=None, description='Proxy details to use for going out to the internet from the connector'
    )
    target_machine: str = Field(description='Target machine on which to install the connector on')
    username: str = Field(description='Username to connect with to the target machine')
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
