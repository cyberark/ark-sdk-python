from typing import Any, Dict, List, Optional, Type

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkServiceActionDefinition(ArkModel):
    action_name: str = Field(description='Action name to be used in the cli commands')
    schemas: Optional[Dict[str, Optional[Type[ArkModel]]]] = Field(
        default=None, description='Schemas for different cli actions for the definition'
    )
    defaults: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description='Defaults for the action schemas parameters')
    async_actions: Optional[List[str]] = Field(default=None, description='List of async actions as part of the schemas')
    subactions: Optional[List['ArkServiceActionDefinition']] = Field(default=None, description='Subactions to this action')


ArkServiceActionDefinition.model_rebuild()
