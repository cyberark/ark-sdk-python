from typing import Any, Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkConnectionCommand(ArkModel):
    command: str = Field(description='The command to actually run')
    expected_rc: int = Field(description='Expected return code', default=0)
    raise_on_error: bool = Field(description='Raise exception on non expected rc', default=True)
    extra_command_data: Dict[str, Any] = Field(description='Extra data for the command', default_factory=dict)
