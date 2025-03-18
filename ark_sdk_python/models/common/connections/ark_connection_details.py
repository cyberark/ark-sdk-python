from enum import Enum
from typing import Final, Optional, Union

from pydantic import Field, IPvAnyAddress
from typing_extensions import Annotated

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.connections.ark_connection_credentials import ArkConnectionCredentials
from ark_sdk_python.models.common.connections.connection_data.ark_ssh_connection_data import ArkSSHConnectionData
from ark_sdk_python.models.common.connections.connection_data.ark_winrm_connection_data import ArkWinRMConnectionData

DEFAULT_CONNECTION_RETRIES: Final[int] = 3
DEFAULT_RETRY_TICK_PERIOD: Final[float] = 5.0


class ArkConnectionType(str, Enum):
    SSH = 'SSH'
    WinRM = 'WinRM'


class ArkConnectionDetails(ArkModel):
    address: Union[str, IPvAnyAddress] = Field(description='Address to connect to')
    port: Annotated[int, Field(ge=0, le=65535)] = Field(description='Port to use for connection', default=22)
    connection_type: ArkConnectionType = Field(description='Type of connection', default=ArkConnectionType.SSH)
    credentials: Optional[ArkConnectionCredentials] = Field(description='Credentials to use for connection', default=None)
    connection_data: Optional[Union[ArkWinRMConnectionData, ArkSSHConnectionData]] = Field(
        description='Extra data to be used for connection', default=None
    )
    connection_retries: int = Field(description='Amount of tries to connect to target', default=DEFAULT_CONNECTION_RETRIES)
    retry_tick_period: float = Field(description='Amount of time to wait between each try', default=DEFAULT_RETRY_TICK_PERIOD)
