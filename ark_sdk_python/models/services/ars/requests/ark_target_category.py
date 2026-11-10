from enum import Enum
from typing import Annotated, Any, Final, FrozenSet

from packaging.version import Version
from pydantic import PlainSerializer, PlainValidator
from pydantic.version import VERSION

from ark_sdk_python.models.common import ArkCategoryType

ARS_SUPPORTED_CATEGORIES: Final[FrozenSet[ArkCategoryType]] = frozenset({ArkCategoryType.CLOUD_CONSOLE, ArkCategoryType.VM})


def _validate_target_category(value: Any) -> ArkCategoryType:
    category = ArkCategoryType.__members__.get(str(value).replace(' ', '_').upper())
    if category not in ARS_SUPPORTED_CATEGORIES:
        raise ValueError(f'Unsupported target category [{value}], supported categories are {[c.name for c in ARS_SUPPORTED_CATEGORIES]}')
    return category


# Versions under 2.9 do not support json_schema_input_type
if Version(VERSION) < Version("2.9"):

    class ArkTargetCategory(str, Enum):
        CLOUD_CONSOLE = 'CLOUD_CONSOLE'
        VM = 'VM'

else:
    ArkTargetCategory = Annotated[
        ArkCategoryType,
        PlainValidator(_validate_target_category, json_schema_input_type=str),
        PlainSerializer(lambda v: v.name),
    ]
