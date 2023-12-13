from typing import List, Optional, Union

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkDPAUserDataAttribute(ArkCamelizedModel):
    name: str = Field(description='Name of the attribute')
    source: Optional[str] = Field(description='Source of the attribute')


class ArkDPAUserData(ArkCamelizedModel):
    roles: Optional[List[Union[str, ArkDPAUserDataAttribute]]] = Field(description='Roles allowed for auth rule', default_factory=list)
    groups: Optional[List[Union[str, ArkDPAUserDataAttribute]]] = Field(description='Groups allowed for auth rule', default_factory=list)
    users: Optional[List[Union[str, ArkDPAUserDataAttribute]]] = Field(description='Users allowed for auth rule', default_factory=list)
