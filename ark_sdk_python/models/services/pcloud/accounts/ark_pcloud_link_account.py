from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudLinkAccount(ArkCamelizedModel):
    account_id: str = Field(description='The id of the account to link')
    safe: str = Field(description='The safe in which the linked account is stored')
    extra_password_index: int = Field(description='The linked account extra password index')
    folder: str = Field(description='Folder of the linked account')
    name: str = Field(description='The linked account name')
