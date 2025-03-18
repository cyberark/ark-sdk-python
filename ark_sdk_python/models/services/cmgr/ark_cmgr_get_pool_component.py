from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrGetPoolComponent(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to get')
    component_id: str = Field(description='ID of the component to get in the pool')
