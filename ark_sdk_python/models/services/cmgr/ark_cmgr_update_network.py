from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrUpdateNetwork(ArkCamelizedModel):
    network_id: str = Field(description='ID of the network to update')
    name: Optional[str] = Field(description='New name of the network to update', default=None)
