from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm import ArkSIAVMSecretType


class ArkSIATargetSetsStats(ArkModel):
    target_sets_count: int = Field(description='Total target sets count')
    target_sets_count_per_secret_type: Dict[ArkSIAVMSecretType, int] = Field(description='Target sets count per secret type')
