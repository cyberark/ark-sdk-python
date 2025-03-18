from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_type import ArkSIADBSecretType
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_store_descriptor import ArkSIADBStoreDescriptor
from ark_sdk_python.models.services.sia.secrets.db.secret_links import ArkSIADBSecretLinks
from ark_sdk_python.models.services.sia.secrets.db.secrets_data import ArkSIADBSecretExposedDataTypes
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag


class ArkSIADBSecretMetadata(ArkModel):
    secret_id: str = Field(description='Secret identifier')
    secret_name: str = Field(description='Name of the secret')
    description: str = Field(description='Description about the secret', default='')
    purpose: str = Field(description='Purpose of the secret', default='')
    secret_type: ArkSIADBSecretType = Field(description='Type of the secret')
    secret_store: ArkSIADBStoreDescriptor = Field(description='Secret store details of the secret')
    secret_link: Optional[ArkSIADBSecretLinks] = Field(default=None, description='Link details of the secret')
    secret_exposed_data: Optional[ArkSIADBSecretExposedDataTypes] = Field(
        default=None, description='Portion of the secret data which can be exposed to the user'
    )
    tags: List[ArkSIADBTag] = Field(description='Tags of the secret', default_factory=list)
    created_by: str = Field(description='Who created the secret')
    creation_time: datetime = Field(description='Creation time of the secret')
    last_updated_by: str = Field(description='Who last updated the secret')
    last_update_time: datetime = Field(description='When was the secret last updated')
    is_active: bool = Field(description='Whether the secret is active or not', default=True)


class ArkSIADBSecretMetadataList(ArkModel):
    total_count: int = Field(description='Total secrets found')
    secrets: List[ArkSIADBSecretMetadata] = Field(description='Actual secrets metadata')
