from pydantic import Field

from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_authorization_rule import ArkDPABaseAuthorizationRule
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_connection_information import ArkDPABaseConnectionInformation
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_connection_data import ArkDPADBConnectAs


class ArkDPADBConnectionInformation(ArkDPABaseConnectionInformation):
    connect_as: ArkDPADBConnectAs = Field(description='In which fashion the connection is made')


class ArkDPADBAuthorizationRule(ArkDPABaseAuthorizationRule):
    connection_information: ArkDPADBConnectionInformation = Field(description='Rule information on how access is made')
