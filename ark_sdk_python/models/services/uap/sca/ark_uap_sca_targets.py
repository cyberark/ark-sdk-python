from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import Field, constr
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPSCAAzureWorkspaceType(str, Enum):
    Directory = 'directory'
    Subscription = 'subscription'
    ResourceGroup = 'resource_group'
    Resource = 'resource'
    ManagementGroup = 'management_group'


class ArkUAPSCAGCPWorkspaceType(str, Enum):
    Organization = 'gcp_organization'
    Folder = 'folder'
    Project = 'project'


class ArkUAPSCAGCPRoleType(IntEnum):
    PreDefined = 0
    Custom = 1
    Basic = 2


class ArkUAPSCABaseTarget(ArkCamelizedModel):
    role_id: str = Field(description='The role id of the target')
    workspace_id: str = Field(description='The workspace id of the target')
    role_name: Optional[str] = Field(default=None, description='The role name of the target')
    workspace_name: Optional[str] = Field(default=None, description='The workspace name of the target')


class ArkUAPSCAOrgTarget(ArkUAPSCABaseTarget):
    org_id: str = Field(description='The organization id of the cloud target')


class ArkUAPSCASCAAWSAccountTarget(ArkUAPSCABaseTarget):
    workspace_id: constr(pattern=r"\w+") = Field(description='The workspace id of the target')


class ArkUAPSCAAWSOrganizationTarget(ArkUAPSCAOrgTarget):
    pass


class ArkUAPSCAAzureTarget(ArkUAPSCAOrgTarget):
    workspace_type: ArkUAPSCAAzureWorkspaceType = Field(description='The type of the workspace in Azure')
    role_type: Optional[ArkUAPSCAGCPRoleType] = Field(description='The type of the role in Azure', default=None)


class ArkUAPSCAGCPTarget(ArkUAPSCAOrgTarget):
    workspace_type: ArkUAPSCAGCPWorkspaceType = Field(description='The type of the workspace in GCP')
    role_package: Optional[str] = Field(default=None, description='The role package of the target')
    role_type: Optional[ArkUAPSCAGCPRoleType] = Field(default=None, description='The type of the role in GCP')


class ArkUAPSCAAWSAccountTarget(ArkUAPSCABaseTarget):
    pass


class ArkUAPSCACloudConsoleTarget(ArkCamelizedModel):
    gcp_targets: Annotated[List[ArkUAPSCAGCPTarget], Field(description='GCP targets list', default_factory=list)]
    azure_targets: Annotated[List[ArkUAPSCAAzureTarget], Field(description='Azure targets list', default_factory=list)]
    aws_organization_targets: Annotated[
        List[ArkUAPSCAAWSOrganizationTarget], Field(description='AWS Organization targets list', default_factory=list)
    ]
    aws_account_targets: Annotated[List[ArkUAPSCAAWSAccountTarget], Field(description='AWS Account targets list', default_factory=list)]


ArkUAPSCAAzureWorkspaceTypesValues: List[str] = [item.value for item in ArkUAPSCAAzureWorkspaceType]

ArkUAPSCAGCPWorkspaceTypesValues: List[str] = [item.value for item in ArkUAPSCAGCPWorkspaceType]
