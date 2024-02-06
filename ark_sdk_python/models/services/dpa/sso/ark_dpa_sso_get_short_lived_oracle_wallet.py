from enum import Enum

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPASSOShortLivedOracleWalletType(str, Enum):
    PEM = 'PEM'
    SSO = 'SSO'


class ArkDPASSOGetShortLivedOracleWallet(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
    unzip_wallet: bool = Field(description='Whether to save zipped or not', default=True)
    folder: str = Field(description='Output folder to write the wallet to')
    wallet_type: ArkDPASSOShortLivedOracleWalletType = Field(
        description='Type of wallet to generate, if PEM, no zip will be generated, only an ewallet.pem file',
        default=ArkDPASSOShortLivedOracleWalletType.SSO,
    )
