from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIAVMSecretsFilter(ArkModel):
    secret_types: Optional[List[ArkSIAVMSecretType]] = Field(default=None, description='Type of secrets to filter')
    name: Optional[str] = Field(default=None, description='Name wildcard to filter with')
    secret_details: Optional[Dict[str, Any]] = Field(default=None, description='Secret details to filter with')
    is_active: Optional[bool] = Field(default=None, description='Filter only active / inactive secrets')
