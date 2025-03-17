from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkProtocolType


def serialize_sia_vm_policies_protocol_type(protocol_type: ArkProtocolType) -> str:
    if isinstance(protocol_type, str):
        protocol_type = ArkProtocolType(protocol_type)
    if protocol_type == ArkProtocolType.SSH:
        return 'ssh'
    if protocol_type == ArkProtocolType.SCP:
        return 'scp'
    if protocol_type == ArkProtocolType.SFTP:
        return 'sftp'
    elif protocol_type == ArkProtocolType.RDP:
        return 'rdp'
    elif protocol_type == ArkProtocolType.HTTPS:
        return 'https'
    raise ArkException('Invalid SIA VM Protocol Type')
