from enum import Enum


class ArkOsType(str, Enum):
    WINDOWS = 'windows'
    DARWIN = 'darwin'
    LINUX = 'linux'
