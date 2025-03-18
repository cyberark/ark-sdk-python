from enum import Enum
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.identity import DirectoryService, RoleAdminRight


class ArkIdentityEntityType(str, Enum):
    Role = 'ROLE'
    User = 'USER'
    Group = 'GROUP'


class ArkIdentityEntity(ArkModel):
    id: str = Field(description='ID of the entity')
    name: str = Field(description='Name of the entity')
    entity_type: ArkIdentityEntityType = Field(description='Type of the entity')
    directory_service_type: DirectoryService = Field(description='Directory type of the entity')
    display_name: Optional[str] = Field(default=None, description='Display name of the entity')
    service_instance_localized: str = Field(description='Display directory service name')


class ArkIdentityUserEntity(ArkIdentityEntity):
    email: Optional[str] = Field(default=None, description='Email of the user')
    description: Optional[str] = Field(default=None, description='Description of the user')


class ArkIdentityGroupEntity(ArkIdentityEntity):
    pass


class ArkIdentityRoleEntity(ArkIdentityEntity):
    admin_rights: Optional[List[RoleAdminRight]] = Field(default=None, description='Admin rights of the role')
    is_hidden: bool = Field(description='Whwether this role is hidden or not')
    description: Optional[str] = Field(default=None, description='Description of the role')
