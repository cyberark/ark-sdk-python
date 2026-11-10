from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkARSGetAccessRequest(ArkCamelizedModel):
    request_id: str = Field(description='The access request id to get')
