from typing import Literal

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.sso.ark_sia_sso_token_type import ArkSIASSOTokenType


class ArkSIASSOGetTokenInfo(ArkModel):
    token_type: ArkSIASSOTokenType = Field(description='Which token type to get the info for')
    service: Literal['DPA-DB', 'DPA-K8S', 'DPA-RDP'] = Field(description='Which service to get the token info for')
