from datetime import datetime
from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkSecretStr
from ark_sdk_python.models.services.pcloud.usermgmt.ark_pcloud_vault_user import ArkPCloudBaseVaultUser


class ArkPCloudUpdateVaultUser(ArkPCloudBaseVaultUser):
    user_id: int = Field(description='ID of the user to update')
    password: Optional[ArkSecretStr] = Field(default=None, description='New password for the user')
    expiry_date: Optional[datetime] = Field(default=None, description='New expiry date of the user')
    enable_user: Optional[bool] = Field(default=None, description='Update whether the user is enabled or not')
    change_password_on_the_next_logon: Optional[bool] = Field(
        default=None, description='Update whether the user needs to change its password on next logon'
    )
    password_never_expires: Optional[bool] = Field(default=None, description='Update whether the password of the user never expires')
