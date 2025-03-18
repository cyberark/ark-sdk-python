from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrDeletePool(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to delete')
