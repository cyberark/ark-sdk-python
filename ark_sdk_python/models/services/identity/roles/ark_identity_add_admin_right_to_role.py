from typing import Optional

from pydantic import Field, conlist

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.identity.roles.ark_identity_admin_right import ArkIdentityAdminRights


class ArkIdentityAddAdminRightsToRole(ArkModel):
    role_id: Optional[str] = Field(description='Role id to add admin rights to')
    role_name: Optional[str] = Field(description='Role name to add admin rights to')
    admin_rights: conlist(ArkIdentityAdminRights, min_items=1) = Field(description='Admin rights to add to the role')
