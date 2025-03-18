from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.cmgr.ark_cmgr_pool_component import ArkCmgrPoolComponentType


class ArkCmgrPoolType(str, Enum):
    PLATFORM = 'PLATFORM'
    ACCESS = 'ACCESS'


class ArkCmgrPool(ArkCamelizedModel):
    id: str = Field(description='ID of the pool')
    name: str = Field(description='Name of the pool')
    description: Optional[str] = Field(description='Description of the pool', default=None)
    assigned_network_ids: List[str] = Field(description='Assigned networks of the pool', default_factory=list)
    identifiers_count: Optional[int] = Field(description='Count of identifiers on the pool', default=None)
    components_count: Optional[Dict[ArkCmgrPoolComponentType, int]] = Field(description='Count of components on the pool', default=None)
    created_at: str = Field(description='The creation time of the pool')
    updated_at: str = Field(description='The last update time of the pool')
