from enum import Enum


class ArkCategoryType(str, Enum):
    CLOUD_CONSOLE = 'Cloud console'
    VM = 'VM'
    DB = 'DB'
