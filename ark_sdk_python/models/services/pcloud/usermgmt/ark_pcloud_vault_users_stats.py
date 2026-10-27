from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.usermgmt.ark_pcloud_vault_user import ArkPCloudVaultAuthMethod


class ArkPCloudVaultUsersStats(ArkModel):
    users_count: int = Field(description='Overall vault users count')
    users_auth_methods_count: Dict[ArkPCloudVaultAuthMethod, int] = Field(description='Vault users count per auth method')
    users_types_count: Dict[str, int] = Field(description='Users count per user type')
