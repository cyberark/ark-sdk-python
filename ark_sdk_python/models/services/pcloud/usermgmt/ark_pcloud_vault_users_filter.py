from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudVaultUsersFilter(ArkModel):
    search: Optional[str] = Field(default=None, description='Search string, matches the username, first name and last name')
    sort: Optional[str] = Field(default=None, description='Sort by value')
    user_type: Optional[str] = Field(default=None, description='Filter by user type')
    component_user: Optional[bool] = Field(default=None, description='Filter whether the user is a component user or not')
    user_name: Optional[str] = Field(default=None, description='Filter by username')
    extended_details: bool = Field(
        default=True, description='Whether to also return the user groups and the DN, a lighter response without them'
    )
    page_size: Optional[int] = Field(
        default=None, ge=1, description='How many users to request per call, the listing pages through all the users in pages of this size'
    )
    page_offset: Optional[int] = Field(
        default=None, ge=0, description='Index of the first user to list, to start or resume the listing from'
    )
