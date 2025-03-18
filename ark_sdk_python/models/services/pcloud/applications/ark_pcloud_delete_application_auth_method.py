from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDeleteApplicationAuthMethod(ArkModel):
    app_id: str = Field(description='ID of the app to delete the auth method from')
    auth_id: str = Field(description='ID of the auth method to delete')
