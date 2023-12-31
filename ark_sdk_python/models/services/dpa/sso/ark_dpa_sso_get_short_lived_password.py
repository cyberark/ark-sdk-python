from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPASSOGetShortLivedPassword(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
