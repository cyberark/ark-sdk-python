from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIAVMSecretInfo(ArkModel):
    secret_id: str = Field(description="ID of the secret")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID of the secret")
    secret_type: ArkSIAVMSecretType = Field(description="Type of the secret")
    secret_name: Optional[str] = Field(default=None, description="A friendly name label")
    secret_details: Dict[str, Any] = Field(description="Secret extra details", default_factory=dict)
    is_active: bool = Field(description="Whether this secret is active or not")
