from typing import Literal, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrPoolsCommonFilter(ArkModel):
    projection: Literal['BASIC', 'EXTENDED'] = Field(description='Type of projection for the response', default='BASIC')
    sort: Optional[str] = Field(description='Sort by given parameter', default=None)
    filter: Optional[str] = Field(description='Filter parameters', default=None)
    order: Optional[Literal['ASC', 'DESC']] = Field(description='Response sort order', default=None)
    page_size: Optional[int] = Field(description='Size of page', default=None)
