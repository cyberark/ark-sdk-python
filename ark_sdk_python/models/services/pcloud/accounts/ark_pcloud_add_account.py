from pydantic import Field, SecretStr

from ark_sdk_python.models.services.pcloud.accounts.ark_pcloud_account import ArkPCloudBaseAccount


class ArkPCloudAddAccount(ArkPCloudBaseAccount):
    secret: SecretStr = Field(description='The secret of the account')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value()}
