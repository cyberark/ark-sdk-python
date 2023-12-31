from typing import Sequence

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkDPADBTag(ArkCamelizedModel):
    key: str = Field(description='Key of the tag, for example environment')
    value: str = Field(description='Value of the tag, for example production')


class ArkDPADBTagList(ArkCamelizedModel):
    tags: Sequence[ArkDPADBTag] = Field(description='List of tags')
    count: int = Field(description='The amount of tags listed')
