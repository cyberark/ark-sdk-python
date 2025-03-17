from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudSafesFilters(ArkModel):
    search: Optional[str] = Field(description='Search by string', default=None)
    sort: Optional[str] = Field(description='Sort results by given key', default=None)
    offset: Optional[int] = Field(description='Offset to the safes list', default=None)
    limit: Optional[int] = Field(description='Limit of results', default=None)
