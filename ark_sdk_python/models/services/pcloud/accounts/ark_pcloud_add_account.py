from pydantic import Field

from ark_sdk_python.models.ark_model import ArkSecretStr
from ark_sdk_python.models.services.pcloud.accounts.ark_pcloud_account import ArkPCloudBaseAccount


class ArkPCloudAddAccount(ArkPCloudBaseAccount):
    secret: ArkSecretStr = Field(description='The secret of the account')
