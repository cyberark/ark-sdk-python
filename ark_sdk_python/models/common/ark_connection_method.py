# pylint: disable=invalid-name
from enum import Enum


class ArkConnectionMethod(str, Enum):
    Standing = 'standing'
    Dynamic = 'dynamic'
