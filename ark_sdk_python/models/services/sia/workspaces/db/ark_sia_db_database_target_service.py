from typing import Optional, Union

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIADBDatabaseTargetService(ArkModel):
    service_name: str = Field(description='Name of the service within the database')
    port: Optional[int] = Field(
        default=None, description='Port of the database service, if not given, the default one will be used', ge=1, le=65535
    )
    secret_id: Optional[str] = Field(
        default=None, description='Secret identifier stored in the secret service related to this database service'
    )


ArkSIADBDatabaseTargetServiceTypes = Union[str, ArkSIADBDatabaseTargetService]
