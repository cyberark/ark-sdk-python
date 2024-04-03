from typing import Any, Dict, List, Optional, Union

from pydantic import Field, root_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkDPADB(ArkCamelizedModel):
    pass


class ArkDPADBIdentifiers(ArkDPADB):
    resources: List[str] = Field(description='Base resource / asset name')


class ArkDPADBMSSQL(ArkDPADBIdentifiers):
    pass


class ArkDPADBMySQL(ArkDPADBIdentifiers):
    pass


class ArkDPADBMariaDB(ArkDPADBIdentifiers):
    pass


class ArkDPADBPostgres(ArkDPADBIdentifiers):
    pass


class ArkDPADBMongo(ArkDPADBIdentifiers):
    pass


class ArkDPADBDb2(ArkDPADBIdentifiers):
    pass


class ArkDPADBOracleResource(ArkCamelizedModel):
    name: str = Field(description='Name of the oracle db resource / asset')
    services: Optional[List[str]] = Field(description='Oracle services in the database')


class ArkDPADBOracle(ArkDPADB):
    resources: List[Union[str, ArkDPADBOracleResource]] = Field(description='List of oracle resources / assets for the policy')


class ArkDPADBProvidersData(ArkCamelizedModel):
    mssql: Optional[ArkDPADBMSSQL] = Field(description='MSSQL related resources')
    mysql: Optional[ArkDPADBMySQL] = Field(description='MySQL related resources')
    mariadb: Optional[ArkDPADBMariaDB] = Field(description='MariaDB related resources')
    postgres: Optional[ArkDPADBPostgres] = Field(description='PostgreSQL related resources')
    oracle: Optional[ArkDPADBOracle] = Field(description='Oracle related resources')
    mongo: Optional[ArkDPADBMongo] = Field(description='Mongo related resources')
    db2: Optional[ArkDPADBDb2] = Field(description='Db2 related resources')

    @root_validator
    @classmethod
    def validate_min_providers(cls, data: Dict) -> Dict[str, Any]:
        if isinstance(data, dict):
            if all(value is None for value in data.values()):
                raise ValueError('policy should contain at least one provider')
        return data
