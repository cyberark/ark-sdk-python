from typing import List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrAddPool(ArkCamelizedModel):
    name: str = Field(description='Name of the pool to add')
    description: Optional[str] = Field(description='Pool description', default=None)
    assigned_network_ids: Annotated[List[str], Field(min_length=1)] = Field(description='Assigned networks to the pool')
