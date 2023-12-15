from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPASSOGetShortLivedOracleWallet(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
    unzip_wallet: bool = Field(description='Whether to save zipped or not', default=True)
    folder: str = Field(description='Output folder to write the wallet to')
