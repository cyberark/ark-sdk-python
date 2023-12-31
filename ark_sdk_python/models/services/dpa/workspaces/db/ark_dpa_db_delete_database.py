from typing import Optional

from pydantic import Field, root_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkDPADBDeleteDatabase(ArkCamelizedModel):
    id: Optional[int] = Field(description='Database id to delete')
    name: Optional[str] = Field(description='Database name to delete')

    # pylint: disable=no-self-use,no-self-argument
    @root_validator
    def validate_either(cls, values):
        if 'id' not in values and 'name' not in values:
            raise ValueError('Either id or name needs to be provided')
        return values
