from typing import Final, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common.identity import DirectoryService
from ark_sdk_python.models.services.identity.directories.ark_identity_entity import ArkIdentityEntityType

DEFAULT_ENTITIES_PAGE_SIZE: Final[int] = 10000
DEFAULT_ENTITIES_LIMIT: Final[int] = 10000
DEFAULT_MAX_PAGE_SIZE: Final[int] = -1


class ArkIdentityListDirectoriesEntities(ArkModel):
    directories: Optional[List[DirectoryService]] = Field(default=None, description='Directories to search on')
    entity_types: Optional[List[ArkIdentityEntityType]] = Field(default=None, description='Member types to search')
    search: Optional[str] = Field(default=None, description='Search string to use')
    page_size: int = Field(description='Page size to emit', default=DEFAULT_ENTITIES_PAGE_SIZE)
    limit: int = Field(description='Limit amount to list', default=DEFAULT_ENTITIES_LIMIT)
    max_page_count: int = Field(description='Max page count to reach to', default=DEFAULT_MAX_PAGE_SIZE)
