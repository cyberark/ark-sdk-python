from typing import List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrUpdatePool(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to update')
    name: Optional[str] = Field(description='Name of the pool to update', default=None)
    description: Optional[str] = Field(description='Pool description to update', default=None)
    assigned_network_ids: Optional[Annotated[List[str], Field(min_length=1)]] = Field(
        description='Assigned networks to the pool to update', default=None
    )
