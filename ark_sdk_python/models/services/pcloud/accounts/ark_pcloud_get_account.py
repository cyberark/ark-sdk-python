from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetAccount(ArkModel):
    account_id: str = Field(description='The id of the account to retrieve')
