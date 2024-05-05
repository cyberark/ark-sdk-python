from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudUnlinkAccount(ArkCamelizedModel):
    account_id: str = Field(description='The id of the account to unlink')
    extra_password_index: str = Field(description='The linked account extra password index')
