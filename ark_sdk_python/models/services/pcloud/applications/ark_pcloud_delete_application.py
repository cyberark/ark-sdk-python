from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDeleteApplication(ArkModel):
    app_id: str = Field(description='ID of the app to delete')
