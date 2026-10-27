from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.identity import DirectoryService


class ArkIdentityDirectory(ArkModel):
    directory: DirectoryService = Field(description='Name of the directory')
    directory_service_uuid: str = Field(description='ID of the directory')
    config: Optional[str] = Field(default=None, description='Configuration name of the directory, such as the domain or the directory name')
    display_name: Optional[str] = Field(default=None, description='Short display name of the directory')
