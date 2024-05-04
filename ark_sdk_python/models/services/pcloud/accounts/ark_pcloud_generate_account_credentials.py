from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGenerateAccountCredentials(ArkModel):
    account_id: str = Field(description='The id of the account to generate the password for')
