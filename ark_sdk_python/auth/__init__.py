import itertools
from typing import Dict, Final, List, Set, Type

from ark_sdk_python.auth.ark_auth import ArkAuth
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.models.auth.ark_auth_method import ArkAuthMethod

SUPPORTED_AUTHENTICATORS_LIST: Final[List[Type[ArkAuth]]] = [ArkISPAuth]
SUPPORTED_AUTHENTICATORS: Final[Dict[(str, Type[ArkAuth])]] = {auth.authenticator_name(): auth for auth in SUPPORTED_AUTHENTICATORS_LIST}
SUPPORTED_AUTH_METHODS: Final[Set[ArkAuthMethod]] = set(
    itertools.chain.from_iterable([auth.supported_auth_methods() for auth in SUPPORTED_AUTHENTICATORS_LIST])
)
