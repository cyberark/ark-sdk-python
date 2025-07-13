from typing import Literal

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIASSOGetShortLivedPassword(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
    service: Literal['DPA-DB', 'DPA-RDP'] = Field(description='Which service to get the token info for', default='DPA-DB')
