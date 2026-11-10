from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.common.ark_ars_query import ArkARSPaginationQuery


class ArkARSFilter(ArkCamelizedModel):
    pagination: ArkARSPaginationQuery = Field(
        default_factory=ArkARSPaginationQuery, description='Pagination details on the response after the filter'
    )
    filter: Optional[str] = Field(default=None, description='Filter string to perform on the response items')
    extended: bool = Field(description='Whether to return an extended response or not', default=False)
