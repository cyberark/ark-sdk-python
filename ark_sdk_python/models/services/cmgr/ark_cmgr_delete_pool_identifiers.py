from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrDeletePoolIdentifier(ArkCamelizedModel):
    identifier_id: str = Field(description='ID of the identifier to delete')


class ArkCmgrDeletePoolSingleIdentifier(ArkCmgrDeletePoolIdentifier):
    pool_id: str = Field(description='ID of the pool to delete the identifier from')


class ArkCmgrDeletePoolBulkIdentifier(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to delete the identifiers from')
    identifiers: List[ArkCmgrDeletePoolIdentifier] = Field(description='Identifiers to delete')
