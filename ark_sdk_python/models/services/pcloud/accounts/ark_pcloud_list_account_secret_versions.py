from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudListAccountSecretVersions(ArkModel):
    account_id: str = Field(description='The id of the account to retrieve the secret versions for')
    show_temporary: bool = Field(description='Show temporary secrets as well', default=False)
