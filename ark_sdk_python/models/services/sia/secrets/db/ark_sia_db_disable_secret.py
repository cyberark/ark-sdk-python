from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIADBDisableSecret(ArkModel):
    secret_id: Optional[str] = Field(default=None, description='ID of the secret to disable')
    secret_name: Optional[str] = Field(default=None, description='Name of the secret to disable')

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values):
        if 'secret_id' not in values and 'secret_name' not in values:
            raise ValueError('Either secret id or secret name needs to be provided')
        return values
