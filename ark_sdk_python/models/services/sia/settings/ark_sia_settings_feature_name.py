from enum import Enum


class ArkSIASettingsFeatureName(str, Enum):
    ADBMfaCaching = 'ADB_MFA_CACHING'
    CertificateValidation = 'CERTIFICATE_VALIDATION'
    K8SMfaCaching = 'K8S_MFA_CACHING'
    RDPFileTransfer = 'RDP_FILE_TRANSFER'
    RDPKeyboardLayout = 'RDP_KEYBOARD_LAYOUT'
    RDPMfaCaching = 'RDP_MFA_CACHING'
    RDPTokenMfaCaching = 'RDP_TOKEN_MFA_CACHING'
    RDPRecording = 'RDP_RECORDING'
    SSHMfaCaching = 'SSH_MFA_CACHING'
    SSHCommandAudit = 'SSH_COMMAND_AUDIT'
    StandingAccess = 'STANDING_ACCESS'
    LogonSequence = 'LOGON_SEQUENCE'
