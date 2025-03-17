# pylint: disable=invalid-name
from enum import Enum


class ArkSIASSOTokenType(str, Enum):
    Password = 'password'
    ClientCertificate = 'client_certificate'
    OracleWallet = 'oracle_wallet'
    RDPFile = 'rdp_file'
