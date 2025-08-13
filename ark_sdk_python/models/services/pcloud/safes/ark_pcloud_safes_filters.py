from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudSafesFilters(ArkModel):
    search: Optional[str] = Field(default=None, description='Search by string')
    sort: Optional[str] = Field(default=None, description='Sort results by given key')
    offset: Optional[int] = Field(default=None, description='Offset to the safes list')
    limit: Optional[int] = Field(default=None, description='Limit of results')
