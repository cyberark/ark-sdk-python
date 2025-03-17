from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityDeleteUsers(ArkModel):
    user_ids: List[str] = Field(min_length=1, description='User IDs to delete')
