from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.services.sia.secrets.vm.ark_sia_vm_secret_type import ArkSIAVMSecretType


class ArkSIAVMAddSecret(ArkModel):
    secret_name: Optional[str] = Field(default=None, description='Optional name of the secret')
    secret_details: Optional[Dict[str, Any]] = Field(default=None, description='Optional extra details about the secret')
    secret_type: ArkSIAVMSecretType = Field(description='Type of the secret to add, data is picked according to the chosen type')
    is_disabled: bool = Field(description='Whether the secret should be disabled or not', default=False)
    provisioner_username: Optional[str] = Field(default=None, description='If provisioner user type is picked, the username')
    provisioner_password: Optional[ArkSecretStr] = Field(default=None, description='If provisioner user type is picked, the password')
    pcloud_account_safe: Optional[str] = Field(default=None, description='If pcloud account type is picked, the account safe')
    pcloud_account_name: Optional[str] = Field(default=None, description='If pcloud account type is picked, the account name')
