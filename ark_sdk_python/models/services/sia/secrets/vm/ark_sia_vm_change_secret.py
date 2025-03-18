from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr


class ArkSIAVMChangeSecret(ArkModel):
    secret_id: str = Field(description='The secret id to change')
    secret_name: Optional[str] = Field(default=None, description='The new name of the secret')
    secret_details: Optional[Dict[str, Any]] = Field(default=None, description='New secret details to add / change')
    is_disabled: Optional[bool] = Field(default=None, description='Whether to disable the secret')
    provisioner_username: Optional[str] = Field(default=None, description='If provisioner user type secret, the new username')
    provisioner_password: Optional[ArkSecretStr] = Field(default=None, description='If provisioner user type secret, the new password')
    pcloud_account_safe: Optional[str] = Field(default=None, description='If pcloud account type secret, the new account safe')
    pcloud_account_name: Optional[str] = Field(default=None, description='If pcloud account type secret, the new account name')
