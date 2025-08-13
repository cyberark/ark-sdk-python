from enum import Enum
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPSCACloudInvalidWorkspaceStatus(str, Enum):
    REMOVED = "REMOVED"
    SUSPENDED = "SUSPENDED"


class ArkUAPSCACloudInvalidWorkspace(ArkCamelizedModel):
    id: str = Field(description="Resource ID")
    status: ArkUAPSCACloudInvalidWorkspaceStatus = Field(description="Workspace status")


class ArkUAPSCACloudInvalidRole(ArkCamelizedModel):
    id: str = Field(description="Invalid role ID")


class ArkUAPSCACloudInvalidWebapp(ArkCamelizedModel):
    id: str = Field(description="Invalid webapp ID")


class ArkUAPSCACloudInvalidResources(ArkCamelizedModel):
    workspaces: Optional[List[ArkUAPSCACloudInvalidWorkspace]] = Field(default=None, description="List of invalid workspaces")
    roles: Optional[List[ArkUAPSCACloudInvalidRole]] = Field(default=None, description="List of invalid roles")
    webapps: Optional[List[ArkUAPSCACloudInvalidWebapp]] = Field(default=None, description="List of invalid webapps")
