from typing import Final, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType

HTTP_PREFIX: Final[str] = 'http://'
HTTPS_PREFIX: Final[str] = 'https://'
HTTPS_PORT: Final[int] = 443


class ArkSIAGetConnectorSetupScript(ArkModel):
    connector_type: ArkWorkspaceType = Field(
        description='The type of the platform for the connector to be installed in', default=ArkWorkspaceType.AWS
    )
    connector_os: ArkOsType = Field(
        description='The type of the operating system for the connector to be installed on', default=ArkOsType.LINUX
    )
    connector_pool_id: Optional[str] = Field(
        description='The connector pool which the connector will be part of, '
        'if not given, the connector will be assigned to the default one',
        default='',
    )
    expiration_minutes: Optional[int] = Field(
        default=15,
        description='The number of minutes the connector setup script will be valid for',
        ge=15,
        le=240,
    )
    proxy_host: Optional[str] = Field(default='', description='The proxy host to use in this connector.')
    proxy_port: Optional[int] = Field(default=443, description='The proxy port to use in this connector.')
    windows_installation_path: Optional[str] = Field(default='', description='The installation path for the connector on Windows machines')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connector_type', mode="before")
    @classmethod
    def validate_connector_type(cls, val):
        if val is not None:
            if ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.FAULT,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val

    # pylint: disable=no-self-argument,no-self-use
    @field_validator('proxy_host')
    def proxy_host_validator(cls, value: str) -> str:
        if not value:
            return ''
        value = value.strip()
        if not value:
            return ''
        if value.startswith(HTTPS_PREFIX):
            value = value.replace(HTTPS_PREFIX, '')
        elif value.startswith(HTTP_PREFIX):
            value = value.replace(HTTP_PREFIX, '')
        if not value:
            return ''
        value = f'{HTTP_PREFIX}{value}'
        return value

    # pylint: disable=no-self-argument,no-self-use
    @field_validator('proxy_port')
    def proxy_port_validator(cls, value: int) -> int:
        if not value:
            return HTTPS_PORT
        if value <= 0:
            raise ValueError('Proxy port must be a positive number')
        return value
