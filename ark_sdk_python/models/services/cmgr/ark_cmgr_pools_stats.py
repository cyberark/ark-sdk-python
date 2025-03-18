from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.cmgr.ark_cmgr_pool_component import ArkCmgrPoolComponentType


class ArkCmgrPoolsStats(ArkModel):
    pools_count: int = Field(description='Overall count of pools')
    networks_count_per_pool: Dict[str, int] = Field(description='Count of networks for each pool')
    identifiers_count_per_pool: Dict[str, int] = Field(description='Count of identifiers for each pool')
    components_count_per_pool: Dict[str, Dict[ArkCmgrPoolComponentType, int]] = Field(description='Count of components for each pool')
