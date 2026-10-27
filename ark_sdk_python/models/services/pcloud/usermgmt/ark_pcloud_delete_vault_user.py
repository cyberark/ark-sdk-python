from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDeleteVaultUser(ArkModel):
    user_id: int = Field(description='ID of the user to delete')
