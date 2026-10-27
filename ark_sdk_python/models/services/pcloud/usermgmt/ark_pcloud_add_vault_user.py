from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkSecretStr
from ark_sdk_python.models.services.pcloud.usermgmt.ark_pcloud_vault_user import ArkPCloudBaseVaultUser, ArkPCloudVaultAuthMethod


class ArkPCloudAddVaultUser(ArkPCloudBaseVaultUser):
    initial_password: ArkSecretStr = Field(description='Initial password for the user')
    expiry_date: Optional[datetime] = Field(default=None, description='Expiry date of the user')
    enable_user: bool = Field(description='Whether the user is enabled from the get-go or not', default=True)
    authentication_method: List[ArkPCloudVaultAuthMethod] = Field(
        description='Authentication method of the user', default_factory=lambda: [ArkPCloudVaultAuthMethod.AuthTypePass]
    )
    change_pass_on_next_logon: bool = Field(description='Whether the user requires to change password on next logon', default=True)
    password_never_expires: bool = Field(description='Whether password never expires', default=False)
