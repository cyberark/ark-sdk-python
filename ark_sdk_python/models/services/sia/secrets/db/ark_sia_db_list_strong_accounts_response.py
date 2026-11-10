from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_metadata import ArkSIADBStrongAccountMetadata


class ArkSIADBListStrongAccountsResponse(ArkCamelizedModel):
    """
    Internal model for parsing the API response structure.
    """

    items: List[ArkSIADBStrongAccountMetadata] = Field(description='List of strong account metadata')
    next_cursor: Optional[str] = Field(default=None, description='Cursor for next page, None if no more results')
    total_count: int = Field(description='Total count of all database strong accounts')
