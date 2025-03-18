from enum import Enum

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.ark_connection_method import ArkConnectionMethod


class ArkSIADBAssetsResponseFormat(str, Enum):
    RAW = 'raw'
    JSON = 'json'


class ArkSIADBBaseGenerateAssets(ArkModel):
    connection_method: ArkConnectionMethod = Field(
        description='Whether to generate assets for standing or dynamic access', default=ArkConnectionMethod.Standing
    )
    response_format: ArkSIADBAssetsResponseFormat = Field(
        description='In which format to return the assets', default=ArkSIADBAssetsResponseFormat.RAW
    )
    folder: str = Field(description='Where to output the assets')
