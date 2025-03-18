from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr


class ArkPCloudAccountCredentials(ArkModel):
    account_id: str = Field(description='The id of the account')
    password: ArkSecretStr = Field(description='The credentials')
