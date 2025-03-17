from enum import Enum


class ArkAccessMethod(str, Enum):
    VAULTED = 'Vaulted'
    JIT = 'JIT'
    Unknown = 'Unknown'
