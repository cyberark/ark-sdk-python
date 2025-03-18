from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrGetNetwork(ArkCamelizedModel):
    network_id: str = Field(description='ID of the network to get')
