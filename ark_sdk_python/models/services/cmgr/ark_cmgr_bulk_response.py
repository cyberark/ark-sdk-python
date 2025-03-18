from http import HTTPStatus
from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrBulkResponse(ArkCamelizedModel):
    body: Optional[Dict[str, Any]] = Field(description='Response body of the request')
    status_code: HTTPStatus = Field(description='Status code of the response')


class ArkCmgrBulkResponses(ArkCamelizedModel):
    responses: Dict[str, ArkCmgrBulkResponse] = Field(description='Responses of the bulk request')
