from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkAccessAssetsAsset(ArkCamelizedModel):
    # identifiers
    asset_category: str = Field(description='The category of the asset')
    asset_type: str = Field(description='The type of the asset')
    asset_id: str = Field(description='Asset identifier')

    # metadata fields
    last_accessed: Optional[str] = Field(default=None, description='The date and time when the asset was last accessed (ISO 8601 format)')
    is_favorite: bool = Field(default=False, description='Is the asset marked as a favorite')
    link_type: Optional[str] = Field(default=None, description='The link type of the asset')
    link_uid: Optional[str] = Field(default=None, description='The UID of the base asset this asset is linked to')

    # general connection fields
    protocol: Optional[str] = Field(default=None, description='The infrastructure asset protocol')
    access_method: Optional[str] = Field(default=None, description='The access method to the infrastructure asset')
    address: Optional[str] = Field(default=None, description='The infrastructure asset address/ID')
    domain: Optional[str] = Field(default=None, description='The infrastructure asset domain')
    network_name: Optional[str] = Field(default=None, description='The infrastructure asset network name')
    platform_type: Optional[str] = Field(default=None, description='The infrastructure asset platform type')

    # vaulted fields
    username: Optional[str] = Field(default=None, description='The infrastructure asset username')
    platform_id: Optional[str] = Field(default=None, description='The infrastructure asset platform identifier')
    platform_subtype: Optional[str] = Field(default=None, description='The infrastructure asset platform subtype')
    workflow_status: Optional[Dict[str, Any]] = Field(default=None, description='The infrastructure asset workflow status')
    file_categories: Optional[Dict[str, Any]] = Field(default=None, description='The infrastructure asset file categories')
    jit_elevate_vaulted_cred: Optional[bool] = Field(
        default=None,
        description='Indicates whether Just-in-Time (JIT) credential elevation is enabled for this vaulted infrastructure asset',
    )

    # discovery zsp fields
    os_type: Optional[str] = Field(default=None, description='The infrastructure asset operating system')
    protocols: Optional[Dict[str, str]] = Field(
        default=None, description='The infrastructure asset protocols and their permissions for Discovery ZSP assets'
    )
    ips: Optional[List[str]] = Field(default=None, description='The infrastructure asset IPs')
    workspace_id: Optional[str] = Field(default=None, description='The infrastructure asset workspace identifier')
    location_type: Optional[str] = Field(default=None, description='The infrastructure asset location')

    # identity fields
    name: Optional[str] = Field(default=None, description='The Identity asset name')
    icon: Optional[str] = Field(default=None, description='The Identity asset icon URL')
    is_sca_enabled: Optional[bool] = Field(
        default=None, description='Indicates whether SCA (Secure Cloud Access) is enabled for the asset application'
    )
    is_sws_enabled: Optional[bool] = Field(
        default=None, description='Indicates whether SWS (Secure Web Sessions) is enabled for the asset application'
    )
    is_launch_disabled: Optional[bool] = Field(default=None, description='Indicates if launch is disabled for the Identity application')

    # Manual ZSP fields
    selected_token_option: Optional[str] = Field(default=None, description='Selected token option')
    network_id: Optional[str] = Field(default=None, description='Network ID')
