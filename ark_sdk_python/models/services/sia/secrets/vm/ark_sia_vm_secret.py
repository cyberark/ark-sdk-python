from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretBytes
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIAVMDataMessage(ArkModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()), description='Data Message ID')
    data: str = Field(description='Actual data')


class ArkSIAVMSecretData(ArkModel):
    secret_data: Union[ArkSecretBytes, ArkSIAVMDataMessage, Dict, str] = Field(
        description="Actual secret data, can be of different types, "
        "and is base64 encoded if of SecretBytes, "
        "Otherwise Stored in the jit data message as a string"
        "Or as a dict of secret data to be encrypted"
    )
    tenant_encrypted: bool = Field(description="Whether this secret is encrypted by the tenant key or not", default=False)


class ArkSIAVMSecret(ArkModel):
    secret_id: str = Field(description="ID of the secret", default_factory=lambda: str(uuid4()))
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID of the secret")
    secret: Optional[ArkSIAVMSecretData] = Field(default=None, description="Secret itself")
    secret_type: ArkSIAVMSecretType = Field(description="Type of the secret")
    secret_details: Dict[str, Any] = Field(description="Secret extra details", default_factory=dict)
    is_active: bool = Field(description="Whether this secret is active or not and can be retrieved or modified", default=True)
    is_rotatable: bool = Field(description="Whether this secret can be rotated", default=True)
    creation_time: datetime = Field(description="Creation time of the secret", default_factory=datetime.utcnow)
    last_modified: datetime = Field(description="Last time the secret was modified", default_factory=datetime.utcnow)
    secret_name: Optional[str] = Field(default=None, description="A friendly name label")
