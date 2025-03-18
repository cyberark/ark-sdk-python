from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIADBGetDatabase(ArkCamelizedModel):
    id: Optional[int] = Field(default=None, description='Database id to get')
    name: Optional[str] = Field(default=None, description='Database name to get')

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values):
        if 'id' not in values and 'name' not in values:
            raise ValueError('Either id or name needs to be provided')
        return values
