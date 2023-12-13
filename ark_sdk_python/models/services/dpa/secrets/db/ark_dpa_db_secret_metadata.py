from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_secret_type import ArkDPADBSecretType
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_store_descriptor import ArkDPADBStoreDescriptor
from ark_sdk_python.models.services.dpa.secrets.db.secret_links import ArkDPADBSecretLinks
from ark_sdk_python.models.services.dpa.secrets.db.secrets_data import ArkDPADBSecretExposedDataTypes
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBSecretMetadata(ArkModel):
    secret_id: str = Field(description='Secret identifier')
    secret_name: str = Field(description='Name of the secret')
    description: str = Field(description='Description about the secret', default='')
    purpose: str = Field(description='Purpose of the secret', default='')
    secret_type: ArkDPADBSecretType = Field(description='Type of the secret')
    secret_store: ArkDPADBStoreDescriptor = Field(description='Secret store details of the secret')
    secret_link: Optional[ArkDPADBSecretLinks] = Field(description='Link details of the secret')
    secret_exposed_data: Optional[ArkDPADBSecretExposedDataTypes] = Field(
        description='Portion of the secret data which can be exposed to the user'
    )
    tags: List[ArkDPADBTag] = Field(description='Tags of the secret', default_factory=list)
    created_by: str = Field(description='Who created the secret')
    creation_time: datetime = Field(description='Creation time of the secret')
    last_updated_by: str = Field(description='Who last updated the secret')
    last_update_time: datetime = Field(description='When was the secret last updated')
    is_active: bool = Field(description='Whether the secret is active or not', default=True)


class ArkDPADBSecretMetadataList(ArkModel):
    total_count: int = Field(description='Total secrets found')
    secrets: List[ArkDPADBSecretMetadata] = Field(description='Actual secrets metadata')
