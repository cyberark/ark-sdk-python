from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityConnectorsFilter(ArkModel):
    online: Optional[bool] = Field(default=None, description='Filter only enabled or disabled connectors')
    forest: Optional[str] = Field(default=None, description='Filter connectors by forest')
    dns: Optional[str] = Field(default=None, description='Filter by dns wildcard')
    machine_name: Optional[str] = Field(default=None, description='Filter by machine name wildcard')
    customer_name: Optional[str] = Field(default=None, description='Filter by customer name wildcard')
    version: Optional[str] = Field(default=None, description='Filter by version wildcard')
