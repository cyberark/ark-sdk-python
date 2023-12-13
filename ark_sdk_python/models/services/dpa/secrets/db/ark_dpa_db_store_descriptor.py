from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_store_type import ArkDPADBStoreType


class ArkDPADBStoreDescriptor(ArkModel):
    store_id: Optional[str] = Field(description='ID of the store')
    store_type: Optional[ArkDPADBStoreType] = Field(description='Type of the store')
