from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudImportPlatform(ArkModel):
    platform_zip_path: str = Field(description='Local path to the platform zip file')
