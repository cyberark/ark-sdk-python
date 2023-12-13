from aenum import MultiValueEnum


class ArkProtocolType(str, MultiValueEnum):
    SSH = 'ssh', 'SSH'
    SCP = 'scp', 'SCP'
    SFTP = 'sftp', 'SFTP'
    RDP = 'rdp', 'RDP'
    CLI = 'cli', 'CLI'
    CONSOLE = 'console', 'Console'
    HTTPS = 'https', 'HTTPS'
