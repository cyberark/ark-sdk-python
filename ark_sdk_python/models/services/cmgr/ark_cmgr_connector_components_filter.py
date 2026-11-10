from pydantic import Field

from ark_sdk_python.models.services.cmgr.ark_cmgr_components_filter import ArkCmgrComponentsFilter


class ArkCmgrConnectorComponentsFilter(ArkCmgrComponentsFilter):
    connector_id: str = Field(description='Connector id to grab the components from')
