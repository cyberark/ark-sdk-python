from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkCmgrInstallComponent(ArkPollableModel):
    connector_id: str = Field(description='Connector id to install a component on')
    component_name: str = Field(description='The component name to install')
    version: Optional[str] = Field(description='Version of the component to install', default='latest')
    extra_vars: Optional[Dict[str, Any]] = Field(default=None, description='Extra vars for the component installation')
