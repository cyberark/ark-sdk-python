from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudTargetPlatformsFilter(ArkModel):
    name: Optional[str] = Field(default=None, description='Name wildcard to filter on')
    platform_id: Optional[str] = Field(default=None, description='Platform id wildcard to filter on')
    active: Optional[bool] = Field(default=None, description='Filter by active target platforms')
    system_type: Optional[str] = Field(default=None, description='Filter by system type')
    periodic_verify: Optional[bool] = Field(default=None, description='Filter by if periodic verify is on')
    manual_verify: Optional[bool] = Field(default=None, description='Filter by if manual verify is on')
    periodic_change: Optional[bool] = Field(default=None, description='Filter by if periodic change is on')
    manual_change: Optional[bool] = Field(default=None, description='Filter by if manual change is on')
    automatic_reconcile: Optional[bool] = Field(default=None, description='Filter by if automatic reconcile is on')
    manual_reconcile: Optional[bool] = Field(default=None, description='Filter by if manual reconcile is on')
