from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkOsType


class ArkCmgrProxyDetails(ArkCamelizedModel):
    proxy_address: Optional[str] = Field(default=None, description='Proxy address to use for going out to the internet from the connector')
    proxy_port: Optional[int] = Field(default=None, description='Proxy port to use for going out to the internet from the connector')


class ArkCmgrGetConnectorSetupScript(ArkCamelizedModel):
    os_type: ArkOsType = Field(description='OS Type to generate the setup script for')
    version: Optional[str] = Field(
        default=None, description='The version of the connector to install, if not given, stable version will be installed'
    )
    installation_path: Optional[str] = Field(default=None, description='Where to install the connector on the machine')
    connector_pool_id: Optional[str] = Field(default=None, description='Connector pool id to associate the connector to')
    proxy_details: Optional[ArkCmgrProxyDetails] = Field(
        default=None, description='Proxy details to use for going out to the internet from the connector'
    )
