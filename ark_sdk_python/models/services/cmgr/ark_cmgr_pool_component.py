from enum import Enum
from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrPoolComponentType(str, Enum):
    PLATFORM_CONNECTOR = 'PLATFORM_CONNECTOR'
    ACCESS_CONNECTOR = 'ACCESS_CONNECTOR'


class ArkCmgrPoolComponent(ArkCamelizedModel):
    id: str = Field(description='ID of the component')
    type: ArkCmgrPoolComponentType = Field(description='Type of the component')
    external_id: str = Field(description='External identifier of the component')
    pool_id: Optional[str] = Field(description='Pool id of the pool holding the component', default=None)
    pool_name: Optional[str] = Field(description='Name of the pool holding the component', default=None)
    created_at: Optional[str] = Field(description='The creation time of the component', default=None)
    updated_at: Optional[str] = Field(description='The last update time of the component', default=None)
