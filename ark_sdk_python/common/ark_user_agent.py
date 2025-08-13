from fake_useragent import UserAgent

from ark_sdk_python.common.ark_version import __version__


def user_agent() -> str:
    return UserAgent(browsers=['chrome']).googlechrome + f' Ark-SDK-Python/{__version__}'
