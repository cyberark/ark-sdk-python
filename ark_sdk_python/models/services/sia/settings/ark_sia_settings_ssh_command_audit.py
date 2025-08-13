from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsSSHCommandAudit(ArkCamelizedModel):
    is_command_parsing_for_audit_enabled: Optional[bool] = Field(default=None, description="Is command parsing for audit enabled")
    shell_prompt_for_audit: Optional[str] = Field(default=None, description="The shell prompt used for audit")
