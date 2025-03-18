from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.identity import DirectoryService


class ArkIdentityListDirectories(ArkModel):
    directories: Optional[List[DirectoryService]] = Field(default=None, description='Directories types to list')
