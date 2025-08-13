from aenum import MultiValueEnum


class ArkUAPDelegationClassification(str, MultiValueEnum):
    RESTRICTED = 'Restricted', "restricted", "RESTRICTED"
    UNRESTRICTED = 'Unrestricted', "unrestricted", "UNRESTRICTED"
