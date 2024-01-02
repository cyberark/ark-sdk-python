from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkProtocolType


def serialize_sm_protocol_type(protocol_type: ArkProtocolType) -> str:
    if isinstance(protocol_type, str):
        protocol_type = ArkProtocolType(protocol_type)
    if protocol_type == ArkProtocolType.SSH:
        return 'SSH'
    elif protocol_type == ArkProtocolType.RDP:
        return 'RDP'
    elif protocol_type == ArkProtocolType.CLI:
        return 'CLI'
    elif protocol_type == ArkProtocolType.CONSOLE:
        return 'Console'
    elif protocol_type == ArkProtocolType.HTTPS:
        return 'HTTPS'
    raise ArkException('Invalid SM Protocol Type')
