from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetApplicationAuthMethod(ArkModel):
    app_id: str = Field(description='ID of the app to get the auth method from')
    auth_id: str = Field(description='ID of the auth method to get')
