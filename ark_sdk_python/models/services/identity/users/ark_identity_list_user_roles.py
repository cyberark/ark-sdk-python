from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models import ArkModel


class ArkIdentityListUserRoles(ArkModel):
    user_id: Optional[str] = Field(description='Id of the user to list the roles for', default=None)
    username: Optional[str] = Field(description='Name of the user to list the roles for, used if no id is given', default=None)

    @model_validator(mode='after')
    def validate_user(self) -> 'ArkIdentityListUserRoles':
        if not self.user_id and not self.username:
            raise ValueError('Either user_id or username must be given')
        return self
