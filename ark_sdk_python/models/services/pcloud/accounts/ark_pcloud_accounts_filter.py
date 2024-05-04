from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models import ArkModel


class ArkPCloudAccountsFilter(ArkModel):
    search: Optional[str] = Field(description='Search by string')
    search_type: Optional[Literal['contains', 'startswith']] = Field(description='Search type to filter with')
    sort: Optional[str] = Field(description='Sort results by given key')
    safe_name: Optional[str] = Field(description='Safe name to filter by')
    offset: Optional[int] = Field(description='Offset to the accounts list')
    limit: Optional[int] = Field(description='Limit of results')
