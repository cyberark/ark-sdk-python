from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAVMGetSecret(ArkModel):
    secret_id: str = Field(description='The secret id to get')
