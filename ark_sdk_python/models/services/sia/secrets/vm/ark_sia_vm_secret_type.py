from enum import Enum


class ArkSIAVMSecretType(str, Enum):
    ProvisionerUser = 'ProvisionerUser'
    PCloudAccount = 'PCloudAccount'
