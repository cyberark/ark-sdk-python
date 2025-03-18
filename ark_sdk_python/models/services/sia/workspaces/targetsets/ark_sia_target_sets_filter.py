from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIATargetSetsFilter(ArkModel):
    name: Optional[str] = Field(default=None, description='Name filter wildcard')
    secret_type: Optional[ArkSIAVMSecretType] = Field(default=None, description='Secret type filter')
