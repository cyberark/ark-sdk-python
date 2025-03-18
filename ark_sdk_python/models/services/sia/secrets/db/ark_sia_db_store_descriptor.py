from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_store_type import ArkSIADBStoreType


class ArkSIADBStoreDescriptor(ArkModel):
    store_id: Optional[str] = Field(default=None, description='ID of the store')
    store_type: Optional[ArkSIADBStoreType] = Field(default=None, description='Type of the store')
