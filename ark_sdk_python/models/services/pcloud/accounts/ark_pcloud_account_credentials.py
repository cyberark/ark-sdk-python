from pydantic import Field, SecretStr

from ark_sdk_python.models import ArkModel


class ArkPCloudAccountCredentials(ArkModel):
    account_id: str = Field(description='The id of the account')
    password: SecretStr = Field(description='The credentials')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value()}
