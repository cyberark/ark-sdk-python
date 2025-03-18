from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrNetworksStats(ArkModel):
    networks_count: int = Field(description='Overall count of network')
    pools_count_per_network: Dict[str, int] = Field(description='Count of pools for each network')
