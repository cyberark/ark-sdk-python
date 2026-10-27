from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetVaultUser(ArkModel):
    user_id: int = Field(description='ID of the user to retrieve')
