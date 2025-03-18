from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrListPoolIdentifiers(ArkModel):
    pool_id: str = Field(description='Pool id to get the identifiers for')
