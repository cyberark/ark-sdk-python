from abc import abstractmethod
from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_status import ArkStatus


class ArkAsyncTask(ArkCamelizedModel):
    task_id: str = Field(description='Async task id (for example tenant id and so on)')
    task_error: Optional[str] = Field(default=None, description='Optional task error that occurred and couldnt be handled')

    @abstractmethod
    def task_status(self) -> ArkStatus:
        pass
