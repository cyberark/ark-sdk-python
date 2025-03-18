from typing import Optional

from pydantic import Field, model_validator
from typing_extensions import Self

from ark_sdk_python.models import ArkModel


class ArkIdentityDeleteUser(ArkModel):
    user_id: Optional[str] = Field(default=None, description='User ID to delete')
    username: Optional[str] = Field(default=None, description='Username to delete')

    @model_validator(mode='after')
    def validate_either(self) -> Self:
        if not self.user_id and not self.username:
            raise ValueError('Either user_id or username needs to be provided')
