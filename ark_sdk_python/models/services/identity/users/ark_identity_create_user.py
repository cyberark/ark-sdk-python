import random
import string
from typing import Final, List, Optional

from pydantic import Field, SecretStr

from ark_sdk_python.common import ArkRandomUtils
from ark_sdk_python.models import ArkModel, ArkSecretStr

DEFAULT_ADMIN_ROLES: Final[List[str]] = ["DpaAdmin", 'global auditor', "System Administrator"]


class ArkIdentityCreateUser(ArkModel):
    username: str = Field(
        description='Name of the user to create', default_factory=lambda: f"ark_user_{ArkRandomUtils.random_string(n=10)}"
    )
    display_name: Optional[str] = Field(
        description='Display name of the user',
        default_factory=lambda: f'{ArkRandomUtils.random_string(5).capitalize()} {ArkRandomUtils.random_string(7).capitalize()}',
    )
    email: Optional[str] = Field(
        description='Email of the user', default_factory=lambda: f'{ArkRandomUtils.random_string(6).lower()}@email.com'
    )
    mobile_number: Optional[str] = Field(
        description='Mobile number of the user', default_factory=lambda: f'+44-987-654-{"".join(random.choices(string.digits, k=4))}'
    )
    suffix: Optional[str] = Field(default=None, description='Suffix to use for the username')
    password: ArkSecretStr = Field(
        description='Password of the user', default_factory=lambda: SecretStr(ArkRandomUtils.random_password(n=25))
    )
    roles: List[str] = Field(description='Roles to add the user to', default_factory=DEFAULT_ADMIN_ROLES.copy)
