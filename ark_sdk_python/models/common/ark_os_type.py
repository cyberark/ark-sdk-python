import sys
from enum import Enum


class ArkOsType(str, Enum):
    WINDOWS = 'windows'
    DARWIN = 'darwin'
    LINUX = 'linux'
    K8S_EPHEMERAL = 'k8s-ephemeral'


def running_os() -> ArkOsType:
    if sys.platform in (
        'aix',
        'linux',
    ):
        return ArkOsType.LINUX
    if sys.platform in (
        'win32',
        'cygwin',
    ):
        return ArkOsType.WINDOWS
    if sys.platform in ('darwin',):
        return ArkOsType.DARWIN
    return ArkOsType.LINUX
