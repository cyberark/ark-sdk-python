from typing import List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.identity.roles.ark_identity_admin_right import ArkIdentityAdminRights


class ArkIdentityAddAdminRightsToRole(ArkModel):
    role_id: Optional[str] = Field(default=None, description='Role id to add admin rights to')
    role_name: Optional[str] = Field(default=None, description='Role name to add admin rights to')
    admin_rights: Annotated[List[ArkIdentityAdminRights], Field(min_length=1)] = Field(description='Admin rights to add to the role')
