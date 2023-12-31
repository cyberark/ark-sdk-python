from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkServiceConfig(ArkModel):
    service_name: str = Field(description='Name of the service')
    required_authenticator_names: List[str] = Field(description='Required authenticators for the service to properly work')
    optional_authenticator_names: List[str] = Field(
        description='Optional authenticators for the service for extra capabilities', default_factory=list
    )
