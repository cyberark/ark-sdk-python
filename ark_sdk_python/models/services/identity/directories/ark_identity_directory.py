from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.identity import DirectoryService


class ArkIdentityDirectory(ArkModel):
    directory: DirectoryService = Field(description='Name of the directory')
    directory_service_uuid: str = Field(description='ID of the directory')
