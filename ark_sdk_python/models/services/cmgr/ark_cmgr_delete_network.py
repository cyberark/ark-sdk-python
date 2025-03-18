from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrDeleteNetwork(ArkCamelizedModel):
    network_id: str = Field(description='ID of the network to delete')
