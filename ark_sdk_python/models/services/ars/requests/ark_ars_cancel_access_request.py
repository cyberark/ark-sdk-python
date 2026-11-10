from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkARSCancelAccessRequest(ArkPollableModel):
    request_id: str = Field(description='The access request id to cancel')
    cancel_reason: str = Field(description='What is the reason for the cancel')
