from enum import Enum
from typing import Annotated

from packaging.version import Version
from pydantic import PlainSerializer, PlainValidator
from pydantic.version import VERSION

from ark_sdk_python.models.common import ArkCategoryType

# Versions under 2.9 do not support json_schema_input_type
if Version(VERSION) < Version("2.9"):

    class ArkTargetCategory(str, Enum):
        CLOUD_CONSOLE = 'CLOUD_CONSOLE'
        VM = 'VM'
        DB = 'DB'

else:
    ArkTargetCategory = Annotated[
        ArkCategoryType,
        PlainValidator(lambda v: ArkCategoryType[v.replace(' ', '_').upper()], json_schema_input_type=str),
        PlainSerializer(lambda v: v.name),
    ]
