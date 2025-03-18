from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrNetworkPool(ArkCamelizedModel):
    id: str = Field(description='ID of the pool')
    name: str = Field(description='Name of the pool')


class ArkCmgrNetwork(ArkCamelizedModel):
    id: str = Field(description='ID of the network')
    name: str = Field(description='Name of the network')
    assigned_pools: Optional[List[ArkCmgrNetworkPool]] = Field(description='Assigned pools on this network', default=None)
    created_at: str = Field(description='The creation time of the network')
    updated_at: str = Field(description='The last update time of the network')
