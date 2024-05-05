from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudSetAccountNextCredentials(ArkCamelizedModel):
    account_id: str = Field(description='The id of the account to change the password for')
    new_credentials: str = Field(description='Next credentials to set')
