from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrGetPool(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to get')
