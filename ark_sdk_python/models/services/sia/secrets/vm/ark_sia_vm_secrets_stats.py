from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIAVMSecretsStats(ArkModel):
    secrets_count: int = Field(description='Overall secrets count')
    active_secrets_count: int = Field(description='Overall active secrets count')
    inactive_secrets_count: int = Field(description='Overall inactive secrets count')
    secrets_count_by_type: Dict[ArkSIAVMSecretType, int] = Field(description='Secrets count by type')
