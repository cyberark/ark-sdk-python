from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_secret_type import ArkDPADBSecretType
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_store_type import ArkDPADBStoreType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBSecretsFilter(ArkModel):
    secret_name: Optional[str] = Field(description='Filter by secret name')
    secret_type: Optional[ArkDPADBSecretType] = Field(description='Filter by type')
    store_type: Optional[ArkDPADBStoreType] = Field(description='Filter by store type')
    is_active: Optional[bool] = Field(description='Filter by if secret is active')
    tags: Optional[List[ArkDPADBTag]] = Field(description='Filter by tags')
