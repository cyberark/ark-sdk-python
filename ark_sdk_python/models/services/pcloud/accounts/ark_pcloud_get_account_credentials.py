from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models import ArkModel


class ArkPCloudGetAccountCredentials(ArkModel):
    account_id: str = Field(description='The id of the account to retrieve the credentials for')
    reason: Optional[str] = Field(default=None, description='Reason for retrieving the credentials')
    ticketing_system_name: Optional[str] = Field(default=None, description='Ticketing system name to use for retrieval of the credentials')
    ticket_id: Optional[str] = Field(default=None, description='Ticket id allowing retrieval of the credentials')
    version: Optional[str] = Field(default=None, description='Version of the credentials to retrieve')
    action_type: Optional[Literal['show', 'copy', 'connect']] = Field(description='Action type of the retrieval', default='show')
    machine: Optional[str] = Field(default=None, description='The address of the remote machine to connect to with the credentials')
