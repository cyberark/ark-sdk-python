from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_type import ArkSIADBSecretType
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_store_type import ArkSIADBStoreType


class ArkSIADBSecretsStats(ArkModel):
    secrets_count: int = Field(description='Overall secrets count')
    active_secrets_count: int = Field(description='Overall active secrets count')
    inactive_secrets_count: int = Field(description='Overall inactive secrets count')
    secrets_count_by_secret_type: Dict[ArkSIADBSecretType, int] = Field(description='Secrets count by secret type')
    secrets_count_by_store_type: Dict[ArkSIADBStoreType, int] = Field(description='Secrets count by store type')
