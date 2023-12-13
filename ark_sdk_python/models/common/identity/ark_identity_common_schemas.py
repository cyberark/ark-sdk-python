from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.ark_model import ArkModel


class IdentityApiResponse(ArkModel):
    success: Literal[True] = Field()
    exception: Optional[str] = Field(alias='Exception')
    error_code: Optional[str] = Field(alias='ErrorCode')
    message: Optional[str] = Field(alias='Message')
    error_id: Optional[str] = Field(alias='ErrorID')
