from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.identity.roles.ark_identity_admin_right import ArkIdentityAdminRights


class ArkIdentityCreateRole(ArkModel):
    role_name: str = Field(description='Role name to create')
    description: Optional[str] = Field(default=None, description='Description of the role')
    admin_rights: List[ArkIdentityAdminRights] = Field(description='Admin rights to add to the role', default_factory=list)
