from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetApplication(ArkModel):
    app_id: str = Field(description='ID of the app to get')
