from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIADBStrongAccountsFilter(ArkCamelizedModel):
    """
    Client-side filter parameters for listing strong accounts.

    Attributes:
        store_type: Filter by store type (pam or managed)
        platform: Filter by platform (e.g., PostgreSQL, MySQL, etc.)
        name: Filter by account name (regex pattern)
    """

    store_type: Optional[str] = Field(
        default=None,
        description='Filter by store type (pam or managed)',
    )
    platform: Optional[str] = Field(
        default=None,
        description='Filter by platform (e.g., PostgreSQL, MySQL, MariaDB, MSSql, Oracle, MongoDB, DB2UnixSSH, WinDomain, AWSAccessKeys)',
    )
    name: Optional[str] = Field(
        default=None,
        description='Filter by account name (regex pattern)',
    )
