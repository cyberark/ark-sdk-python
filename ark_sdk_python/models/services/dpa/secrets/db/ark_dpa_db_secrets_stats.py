from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_secret_type import ArkDPADBSecretType
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_store_type import ArkDPADBStoreType


class ArkDPADBSecretsStats(ArkModel):
    secrets_count: int = Field(description='Overall secrets count')
    active_secrets_count: int = Field(description='Overall active secrets count')
    inactive_secrets_count: int = Field(description='Overall inactive secrets count')
    secrets_count_by_secret_type: Dict[ArkDPADBSecretType, int] = Field(description='Secrets count by secret type')
    secrets_count_by_store_type: Dict[ArkDPADBStoreType, int] = Field(description='Secrets count by store type')
