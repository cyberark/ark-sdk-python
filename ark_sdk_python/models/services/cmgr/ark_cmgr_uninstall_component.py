from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkCmgrUninstallComponent(ArkPollableModel):
    """Request model for uninstalling a specific component via the CMS uninstall API."""

    connector_id: str = Field(description="Connector id to uninstall a component from")
    component_id: str = Field(description="Component id to uninstall")
    extra_vars: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional extra variables to pass to the uninstall operation",
    )
