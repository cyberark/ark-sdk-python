from typing import Optional

from pydantic import Field, root_validator

from ark_sdk_python.models.ark_model import ArkModel


class ArkDPADBDisableSecret(ArkModel):
    secret_id: Optional[str] = Field(description='ID of the secret to disable')
    secret_name: Optional[str] = Field(description='Name of the secret to disable')

    # pylint: disable=no-self-use,no-self-argument
    @root_validator
    def validate_either(cls, values):
        if 'secret_id' not in values and 'secret_name' not in values:
            raise ValueError('Either secret id or secret name needs to be provided')
        return values
