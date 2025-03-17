from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_type import ArkSIADBSecretType
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_store_type import ArkSIADBStoreType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag


class ArkSIADBSecretsFilter(ArkModel):
    secret_name: Optional[str] = Field(default=None, description='Filter by secret name')
    secret_type: Optional[ArkSIADBSecretType] = Field(default=None, description='Filter by type')
    store_type: Optional[ArkSIADBStoreType] = Field(default=None, description='Filter by store type')
    is_active: Optional[bool] = Field(default=None, description='Filter by if secret is active')
    tags: Optional[List[ArkSIADBTag]] = Field(default=None, description='Filter by tags')
