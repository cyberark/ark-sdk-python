from enum import Enum
from typing import Dict, Final, List, Optional, Set

from overrides import overrides
from pydantic import Field, StringConstraints, model_validator
from typing_extensions import Annotated, Self

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.db import (
    ArkSIADBMongoDatabaseBuiltinRole,
    ArkSIADBMongoGlobalBuiltinRole,
    ArkSIADBSqlServerDatabaseBuiltinRole,
    ArkSIADBSqlServerGlobalBuiltinRole,
)
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_consts import UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT

DB_PROFILE_MAXIMUM_ENTITIES: Final[int] = 50

LDAP_GROUP_MAX_NAME_LENGTH: Final[int] = 50

DB_ROLE_MAX_LENGTH: Final[int] = 50
DB_USER_MAX_LENGTH: Final[int] = 256

DATABASE_NAME_MAX_LENGTH: Final[int] = 256


SqlServerRole = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DB_ROLE_MAX_LENGTH)]
DatabaseName = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DATABASE_NAME_MAX_LENGTH)]

SqlServerDatabaseCustomRolesList = Annotated[
    List[SqlServerRole],
    Field(
        max_length=DB_PROFILE_MAXIMUM_ENTITIES,
        description='The list of per database specific custom roles to assign to the user upon connecting to the specified database',
    ),
]


def _validate_global_roles(
    global_builtin_roles: List[str],
    global_custom_roles: Optional[List[str]],
    database_builtin_roles: Dict[str, List[Enum]],
    database_custom_roles: Dict[str, List[str]],
) -> None:
    """
    Validates that a MongoDB/SQL Server auth profile has sufficient global(instance) roles
    **Only when no database-specific roles are defined**.

    User experience:
    - If the profile does not have any databases, it must include at least one global role
      (either builtin or custom) to ensure that the instance-level permissions are not empty.
    - If any database is defined, then instance-level roles are optional.

    Note: This function checks the *absence* of DB roles first, because it's only in that case
    that global roles become required.
    """
    if not database_builtin_roles and not database_custom_roles:
        if not global_builtin_roles and not global_custom_roles:
            raise ValueError('At least one global role must be defined when no databases are specified.')


def _validate_databases_roles_logic(
    database_builtin_roles: Dict[str, List[Enum]],
    database_custom_roles: Dict[str, List[str]],
) -> None:
    """
    Validates that each configured database has at least one role (either builtin or custom).

    User experience:
    - If a database is defined, it must have some permissions assigned to it.
    - This prevents users from unintentionally misconfiguring access by adding databases without any roles.

    This function iterates over all defined database names and raises an error if any of them
    have no roles assigned (builtin / custom).
    """
    all_children_db_names: Set[str] = set(database_builtin_roles.keys()) | set(database_custom_roles.keys())

    missing_role_dbs: List[str] = [
        db for db in all_children_db_names if not database_builtin_roles.get(db) and not database_custom_roles.get(db)
    ]

    if missing_role_dbs:
        raise ValueError(
            f'The following databases are missing roles (at least one builtin or custom is required): '
            f'{", ".join(sorted(missing_role_dbs))}'
        )


class ArkUAPSIADBProfile(ArkCamelizedModel):
    # pylint: disable=no-self-use
    def databases_count(self) -> int:
        """
        Returns the number of all databases the defined by the profile.
        """
        return 1


class ArkUAPSIADBLDAPAuthProfile(ArkUAPSIADBProfile):
    assign_groups: Annotated[
        List[Annotated[str, StringConstraints(strict=True, min_length=1, max_length=LDAP_GROUP_MAX_NAME_LENGTH)]],
        Field(min_length=1, max_length=DB_PROFILE_MAXIMUM_ENTITIES, description='The list of LDAP groups to assign to the user'),
    ]


class ArkUAPSIADBLocalDBAuthProfile(ArkUAPSIADBProfile):
    roles: Annotated[
        List[Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DB_ROLE_MAX_LENGTH)]],
        Field(min_length=1, max_length=DB_PROFILE_MAXIMUM_ENTITIES, description='The list of roles to assign to the user'),
    ]


class ArkUAPSIADBOracleDBAuthProfile(ArkUAPSIADBProfile):
    roles: Annotated[
        List[Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DB_ROLE_MAX_LENGTH)]],
        Field(max_length=DB_PROFILE_MAXIMUM_ENTITIES, description='The list of roles to assign to the user'),
    ]
    dba_role: Annotated[bool, Field(description='Whether to assign the DBA role to the user')]
    sysdba_role: Annotated[bool, Field(description='Whether to assign the SYSDBA role to the user')]
    sysoper_role: Annotated[bool, Field(description='Whether to assign the SYSOPER role to the user')]

    @model_validator(mode='after')
    def validate_oracle_roles(self) -> Self:
        if not self.roles and not self.dba_role and not self.sysdba_role and not self.sysoper_role:
            raise ValueError('At least one role must be defined (either a builtin role or a custom role)')

        return self


class ArkUAPSIADBMongoAuthProfile(ArkUAPSIADBProfile):
    global_builtin_roles: Annotated[
        List[ArkSIADBMongoGlobalBuiltinRole],
        Field(max_length=DB_PROFILE_MAXIMUM_ENTITIES, description='The list of global builtin roles to assign to the user'),
    ]
    database_builtin_roles: Annotated[
        Dict[
            DatabaseName,
            Annotated[
                List[ArkSIADBMongoDatabaseBuiltinRole],
                Field(
                    max_length=DB_PROFILE_MAXIMUM_ENTITIES,
                    description='The list of database specific builtin roles to assign to the user upon connecting to the specified database',
                ),
            ],
        ],
        Field(
            max_length=UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT,
            description='The list of database builtin roles to assign to the user, for each database',
        ),
    ]
    database_custom_roles: Annotated[
        Dict[
            DatabaseName,
            Annotated[
                List[Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DB_ROLE_MAX_LENGTH)]],
                Field(
                    max_length=DB_PROFILE_MAXIMUM_ENTITIES,
                    description='The list of database specific custom roles to assign to the user upon connecting to the specified database',
                ),
            ],
        ],
        Field(
            max_length=UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT,
            description='The list of database custom roles to assign to the user, for each database',
        ),
    ]

    @overrides
    def databases_count(self) -> int:
        """
        Returns the number of all databases the defined by the profile.
        It includes all the databases defined by the profile, and the instance itself
        """
        return 1 + len(self.database_custom_roles.keys() | self.database_builtin_roles.keys())

    @model_validator(mode='after')
    def validate_global_roles(self) -> Self:
        _validate_global_roles(
            global_builtin_roles=self.global_builtin_roles,
            global_custom_roles=None,
            database_builtin_roles=self.database_builtin_roles,
            database_custom_roles=self.database_custom_roles,
        )

        return self

    @model_validator(mode='after')
    def validate_databases_roles(self) -> Self:
        _validate_databases_roles_logic(
            database_builtin_roles=self.database_builtin_roles,
            database_custom_roles=self.database_custom_roles,
        )

        return self


class ArkUAPSIADBSqlServerAuthProfile(ArkUAPSIADBProfile):
    global_builtin_roles: Annotated[
        List[ArkSIADBSqlServerGlobalBuiltinRole],
        Field(
            description='The list of global builtin roles to assign to the user',
            default_factory=list,
        ),
    ]
    global_custom_roles: Annotated[
        List[SqlServerRole],
        Field(
            max_length=DB_PROFILE_MAXIMUM_ENTITIES,
            description='The list of global custom roles to assign to the user',
            default_factory=list,
        ),
    ]
    database_builtin_roles: Annotated[
        Dict[
            DatabaseName,
            Annotated[
                List[ArkSIADBSqlServerDatabaseBuiltinRole],
                Field(
                    max_length=DB_PROFILE_MAXIMUM_ENTITIES,
                    description='The list of database specific builtin roles to assign to the user upon connecting to the specified database',
                ),
            ],
        ],
        Field(
            max_length=UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT,
            description='The list of database builtin roles to assign to the user, for each database',
            default_factory=dict,
        ),
    ]
    database_custom_roles: Annotated[
        Dict[
            DatabaseName,
            Annotated[
                List[SqlServerRole],
                Field(
                    max_length=DB_PROFILE_MAXIMUM_ENTITIES,
                    description='The list of per database specific custom roles to assign to the user upon connecting to the specified database',
                ),
            ],
        ],
        Field(
            max_length=UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT,
            description='The list of database custom roles to assign to the user, for each database',
            default_factory=dict,
        ),
    ]

    @overrides
    def databases_count(self) -> int:
        """
        Returns the number of all databases the defined by the profile.
        It includes all the databases defined by the profile, and the instance itself
        """
        return 1 + len(self.database_custom_roles.keys() | self.database_builtin_roles.keys())

    @model_validator(mode='after')
    def validate_global_roles(self) -> Self:
        _validate_global_roles(
            global_builtin_roles=self.global_builtin_roles,
            global_custom_roles=self.global_custom_roles,
            database_builtin_roles=self.database_builtin_roles,
            database_custom_roles=self.database_custom_roles,
        )

        return self

    @model_validator(mode='after')
    def validate_databases_roles(self) -> Self:
        _validate_databases_roles_logic(
            database_builtin_roles=self.database_builtin_roles,
            database_custom_roles=self.database_custom_roles,
        )

        return self


class ArkUAPSIADBRDSIAMUserAuthProfile(ArkUAPSIADBProfile):
    db_user: Annotated[
        Annotated[str, StringConstraints(strict=True, min_length=1, max_length=DB_USER_MAX_LENGTH)],
        Field(description='The IAM user to use for connecting to the database', title='Database IAM User'),
    ]
