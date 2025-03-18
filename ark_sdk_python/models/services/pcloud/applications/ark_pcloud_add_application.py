from datetime import date, timedelta

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkPCloudAddApplication(ArkTitleizedModel):
    app_id: str = Field(description='ID of the application')
    description: str = Field(description='Description of the application', default='')
    location: str = Field(description='Location of the application in the vault', default='\\')
    access_permitted_from: int = Field(description='Start time the access is permitted in hours', default=0)
    access_permitted_to: int = Field(description='End time the access is permitted in hours', default=24)
    expiration_date: str = Field(
        description='Expiratin date of the application in format mm/dd/yyyy',
        default_factory=lambda: (date.today() + timedelta(days=30)).strftime('%m/%d/%Y'),
    )
    disabled: bool = Field(description='Whether application is disabled or not', default=False)
    business_owner_first_name: str = Field(description='First name of the owner', default='', alias='BusinessOwnerFName')
    business_owner_last_name: str = Field(description='Last name of the owner', default='', alias='BusinessOwnerLName')
    business_owner_email: str = Field(description='Email of the owner', default='', alias='BusinessOwnerEmail')
    business_owner_phone: str = Field(description='Phone of the owner', default='', alias='BusinessOwnerPhone')
