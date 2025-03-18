from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrAddNetwork(ArkCamelizedModel):
    name: str = Field(description='Name of the network to add')
