from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudTargetPlatformsFilter(ArkModel):
    name: Optional[str] = Field(description='Name wildcard to filter on', default=None)
    platform_id: Optional[str] = Field(description='Platform id wildcard to filter on', default=None)
    active: Optional[bool] = Field(description='Filter by active target platforms', default=None)
    system_type: Optional[str] = Field(description='Filter by system type', default=None)
    periodic_verify: Optional[bool] = Field(description='Filter by if periodic verify is on', default=None)
    manual_verify: Optional[bool] = Field(description='Filter by if manual verify is on', default=None)
    periodic_change: Optional[bool] = Field(description='Filter by if periodic change is on', default=None)
    manual_change: Optional[bool] = Field(description='Filter by if manual change is on', default=None)
    automatic_reconcile: Optional[bool] = Field(description='Filter by if automatic reconcile is on', default=None)
    manual_reconcile: Optional[bool] = Field(description='Filter by if manual reconcile is on', default=None)
