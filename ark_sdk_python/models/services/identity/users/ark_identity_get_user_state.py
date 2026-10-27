from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models import ArkModel


class ArkIdentityGetUserState(ArkModel):
    user_id: Optional[str] = Field(description='Id of the user to get the state of', default=None)
    username: Optional[str] = Field(description='Name of the user to get the state of, used if no id is given', default=None)
    directory_service_uuid: Optional[str] = Field(description='Directory service of the user, if known', default=None)

    @model_validator(mode='after')
    def validate_user(self) -> 'ArkIdentityGetUserState':
        if not self.user_id and not self.username:
            raise ValueError('Either user_id or username must be given')
        return self
