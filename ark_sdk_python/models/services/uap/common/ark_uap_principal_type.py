from aenum import MultiValueEnum


class ArkUAPPrincipalType(str, MultiValueEnum):
    USER = 'USER', "User", "user"
    ROLE = 'ROLE', "Role", "role"
    GROUP = 'GROUP', "Group", "group"
