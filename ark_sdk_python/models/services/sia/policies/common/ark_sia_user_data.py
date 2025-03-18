from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIAUserDataAttribute(ArkCamelizedModel):
    name: str = Field(description='Name of the attribute')
    source: Optional[str] = Field(default=None, description='Source of the attribute')
    identifier: Optional[str] = Field(default=None, description='Identifier of the attribute')


class ArkSIAUserData(ArkCamelizedModel):
    roles: Optional[List[ArkSIAUserDataAttribute]] = Field(description='Roles allowed for auth rule', default_factory=list)
    groups: Optional[List[ArkSIAUserDataAttribute]] = Field(description='Groups allowed for auth rule', default_factory=list)
    users: Optional[List[ArkSIAUserDataAttribute]] = Field(description='Users allowed for auth rule', default_factory=list)
