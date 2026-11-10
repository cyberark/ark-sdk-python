from enum import Enum
from typing import List, Optional, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkARSSortDirection(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


class ArkARSSortQuery(ArkCamelizedModel):
    direction: Optional[ArkARSSortDirection] = Field(default=None, description='Direction in which to sort the response')
    field: Optional[str] = Field(default=None, description='Which field to sort the response on')


class ArkARSPaginationQuery(ArkCamelizedModel):
    offset: Optional[int] = Field(default=None, description='Offset of the items for the response')
    limit: int = Field(default=1000, description='Limit amount of items for the response')
    sort: Optional[Union[ArkARSSortQuery, List[ArkARSSortQuery]]] = Field(default=None, description='How to sort the response')
