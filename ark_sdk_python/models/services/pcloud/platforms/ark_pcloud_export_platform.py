from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudExportPlatform(ArkModel):
    platform_id: str = Field(description='ID of the platform to export its zip data')
    output_folder: str = Field(description='Output folder path to write the zipped platform data to')
