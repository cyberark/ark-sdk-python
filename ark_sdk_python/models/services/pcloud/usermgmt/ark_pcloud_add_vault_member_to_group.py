from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudAddVaultMemberToGroup(ArkCamelizedModel):
    group_id: Union[int, str] = Field(description='Group id to add the member to')
    member_id: Union[int, str] = Field(description='Member username or domain group name to add to the vault group')
    member_type: Literal['vault', 'domain'] = Field(
        description='Type of the member, defaults to vault, can be domain or vault', default='vault'
    )
    domain_name: Optional[str] = Field(default=None, description='Domain mae in the case of domain member type')
