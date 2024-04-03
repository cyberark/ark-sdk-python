# pylint: disable=invalid-name
from enum import Enum


class ArkDPADBAssetsType(str, Enum):
    OracleTNSAssets = 'oracle_tns_assets'
    ProxyFullChain = 'proxy_full_chain'
