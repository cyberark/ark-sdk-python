from typing import Any, List

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkIdentityUserInfo(ArkTitleizedModel):
    first_name: str = Field(description='First name of the user')
    last_name: str = Field(description='Last name of the user')
    home_number: str = Field(description='Home number of the user')
    manager: str = Field(description='Manager of the user')
    username: str = Field(description='Username info')
    groups: List[Any] = Field(description='AD groups of the user', default_factory=list)
    rights: List[str] = Field(description='Administrative rights of the user', default_factory=list)
    roles: List[Any] = Field(description='Roles of the user', default_factory=list)
