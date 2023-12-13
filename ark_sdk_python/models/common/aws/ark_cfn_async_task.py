from typing import Any

from overrides import overrides
from pydantic import Field

from ark_sdk_python.models.common import ArkAsyncTask, ArkStatus


class ArkCFNAsyncTask(ArkAsyncTask):
    status: ArkStatus = Field(description='CFN Job Async task status')
    stack_name: str = Field(description='Name of the stack')
    stack_target_status: str = Field(description='Target operation of the stack to reach to')
    stack_info: Any = Field(description='Current stack information')

    @overrides
    def task_status(self) -> ArkStatus:
        return self.status
