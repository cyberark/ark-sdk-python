from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.cmgr.ark_cmgr_pool_identifiers import ArkCmgrPoolIdentifierType


class ArkCmgrAddPoolIdentifier(ArkCamelizedModel):
    type: ArkCmgrPoolIdentifierType = Field(description='Type of identifier to add')
    value: str = Field(description='Value of the identifier')


class ArkCmgrAddPoolSingleIdentifier(ArkCmgrAddPoolIdentifier):
    pool_id: str = Field(description='ID of the pool to add the identifier to')


class ArkCmgrAddPoolBulkIdentifier(ArkCamelizedModel):
    pool_id: str = Field(description='ID of the pool to add the identifiers to')
    identifiers: List[ArkCmgrAddPoolIdentifier] = Field(description='Identifiers to add')
