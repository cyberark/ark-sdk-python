from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudSafesFilters(ArkModel):
    search: Optional[str] = Field(description='Search by string')
    sort: Optional[str] = Field(description='Sort results by given key')
    offset: Optional[int] = Field(description='Offset to the safes list')
    limit: Optional[int] = Field(description='Limit of results')
