from typing import Any, Dict, Optional

from pydantic import Field, model_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_adb_mfa_caching import ArkSIASettingsADBMfaCaching
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_certificate_validation import ArkSIASettingsCertificateValidation
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_k8s_mfa_caching import ArkSIASettingsK8SMfaCaching
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_logon_sequence import ArkSIASettingsLogonSequence
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_rdp_file_transfer import ArkSIASettingsRDPFileTransfer
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_rdp_keyboard_layout import ArkSIASettingsRDPKeyboardLayout
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_rdp_mfa_caching import ArkSIASettingsRDPMfaCaching
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_rdp_recording import ArkSIASettingsRDPRecording
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_rdp_token_mfa_caching import ArkSIASettingsRDPTokenMfaCaching
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_ssh_command_audit import ArkSIASettingsSSHCommandAudit
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_ssh_mfa_caching import ArkSIASettingsSSHMfaCaching
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_standing_access import ArkSIASettingsStandingAccess


class ArkSIASettingsSetSettings(ArkCamelizedModel):
    adb_mfa_caching: Optional[ArkSIASettingsADBMfaCaching] = Field(default=None, description="Settings for ADB MFA Caching")
    certificate_validation: Optional[ArkSIASettingsCertificateValidation] = Field(
        default=None, description="Settings for Certificate Validation"
    )
    k8s_mfa_caching: Optional[ArkSIASettingsK8SMfaCaching] = Field(default=None, description="Settings for K8S MFA Caching")
    rdp_file_transfer: Optional[ArkSIASettingsRDPFileTransfer] = Field(default=None, description="Settings for RDP File Transfer")
    rdp_keyboard_layout: Optional[ArkSIASettingsRDPKeyboardLayout] = Field(default=None, description="Settings for RDP Keyboard Layout")
    rdp_mfa_caching: Optional[ArkSIASettingsRDPMfaCaching] = Field(default=None, description="Settings for RDP MFA Caching")
    rdp_token_mfa_caching: Optional[ArkSIASettingsRDPTokenMfaCaching] = Field(
        default=None, description="Settings for RDP Token MFA Caching"
    )
    rdp_recording: Optional[ArkSIASettingsRDPRecording] = Field(default=None, description="Settings for RDP Recording")
    ssh_mfa_caching: Optional[ArkSIASettingsSSHMfaCaching] = Field(default=None, description="Settings for SSH MFA Caching")
    ssh_command_audit: Optional[ArkSIASettingsSSHCommandAudit] = Field(default=None, description="Settings for SSH Command Audit")
    standing_access: Optional[ArkSIASettingsStandingAccess] = Field(default=None, description="Settings for Standing Access")
    logon_sequence: Optional[ArkSIASettingsLogonSequence] = Field(default=None, description="Settings for Logon Sequence")

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if all(value is None for value in values.values()):
            raise ValueError('At least one setting needs to be provided')
        return values
