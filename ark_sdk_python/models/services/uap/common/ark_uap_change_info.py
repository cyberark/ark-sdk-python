from typing import Optional

from pydantic import BaseModel, Field, constr

from ark_sdk_python.models.ark_model import ArkSerializableDatetime


class ArkUAPChangeInfo(BaseModel):
    user: Optional[constr(min_length=1, max_length=512, pattern=r'\w+')] = Field(
        default=None, description='Username of the user who made the change'
    )
    time: Optional[ArkSerializableDatetime] = Field(default=None, description='Time of the change')
