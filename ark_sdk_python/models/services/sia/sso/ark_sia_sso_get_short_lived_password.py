from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIASSOGetShortLivedPassword(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
