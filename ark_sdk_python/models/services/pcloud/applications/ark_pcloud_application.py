from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkPCloudApplication(ArkTitleizedModel):
    app_id: str = Field(description='ID of the application', alias='AppID')
    description: str = Field(description='Description of the application')
    location: str = Field(description='Location of the application in the vault')
    access_permitted_from: int = Field(description='Start time the access is permitted in hours')
    access_permitted_to: int = Field(description='End time the access is permitted in hours')
    expiration_date: str = Field(description='Expiratin date of the application in format mm-dd-yyyy')
    disabled: bool = Field(description='Whether application is disabled or not')
    business_owner_first_name: str = Field(description='First name of the owner', alias='BusinessOwnerFName')
    business_owner_last_name: str = Field(description='Last name of the owner', alias='BusinessOwnerLName')
    business_owner_email: str = Field(description='Email of the owner', alias='BusinessOwnerEmail')
    business_owner_phone: str = Field(description='Phone of the owner', alias='BusinessOwnerPhone')
