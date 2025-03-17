from pydantic import Field

from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_authorization_rule import ArkSIABaseAuthorizationRule
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_connection_information import ArkSIABaseConnectionInformation
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_connection_data import ArkSIADBConnectAs


class ArkSIADBConnectionInformation(ArkSIABaseConnectionInformation):
    connect_as: ArkSIADBConnectAs = Field(description='In which fashion the connection is made')


class ArkSIADBAuthorizationRule(ArkSIABaseAuthorizationRule):
    connection_information: ArkSIADBConnectionInformation = Field(description='Rule information on how access is made')
