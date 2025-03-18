from typing import Any, Dict, List, Optional, Union

from pydantic import Field, model_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIADB(ArkCamelizedModel):
    pass


class ArkSIADBIdentifiers(ArkSIADB):
    resources: List[str] = Field(description='Base resource / asset name')


class ArkSIADBMSSQL(ArkSIADBIdentifiers):
    pass


class ArkSIADBMySQL(ArkSIADBIdentifiers):
    pass


class ArkSIADBMariaDB(ArkSIADBIdentifiers):
    pass


class ArkSIADBPostgres(ArkSIADBIdentifiers):
    pass


class ArkSIADBMongo(ArkSIADBIdentifiers):
    pass


class ArkSIADBDb2(ArkSIADBIdentifiers):
    pass


class ArkSIADBOracleResource(ArkCamelizedModel):
    name: str = Field(description='Name of the oracle db resource / asset')
    services: Optional[List[str]] = Field(default=None, description='Oracle services in the database')


class ArkSIADBOracle(ArkSIADB):
    resources: List[Union[str, ArkSIADBOracleResource]] = Field(description='List of oracle resources / assets for the policy')


class ArkSIADBProvidersData(ArkCamelizedModel):
    mssql: Optional[ArkSIADBMSSQL] = Field(default=None, description='MSSQL related resources')
    mysql: Optional[ArkSIADBMySQL] = Field(default=None, description='MySQL related resources')
    mariadb: Optional[ArkSIADBMariaDB] = Field(default=None, description='MariaDB related resources')
    postgres: Optional[ArkSIADBPostgres] = Field(default=None, description='PostgreSQL related resources')
    oracle: Optional[ArkSIADBOracle] = Field(default=None, description='Oracle related resources')
    mongo: Optional[ArkSIADBMongo] = Field(default=None, description='Mongo related resources')
    db2: Optional[ArkSIADBDb2] = Field(default=None, description='Db2 related resources')

    @model_validator(mode='before')
    @classmethod
    def validate_min_providers(cls, data: Dict) -> Dict[str, Any]:
        if isinstance(data, dict):
            if all(value is None for value in data.values()):
                raise ValueError('policy should contain at least one provider')
        return data
