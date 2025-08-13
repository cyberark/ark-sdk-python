from typing import List

from pydantic import Field, model_validator
from typing_extensions import Annotated, Self

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_consts import UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_instance_target import ArkUAPSIADBInstanceTarget


class ArkUAPSIADBTargets(ArkCamelizedModel):
    instances: Annotated[List[ArkUAPSIADBInstanceTarget], Field(min_length=1, max_length=UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT)]

    @model_validator(mode='after')
    def validate_instances(self) -> Self:
        if len(self.instances) != len({instance.instance_name for instance in self.instances}):
            raise ValueError('Instance names must be unique')
        if len(self.instances) != len({instance.instance_id for instance in self.instances}):
            raise ValueError('Instance ids must be unique')
        return self

    @model_validator(mode='after')
    def limit_items_count(self) -> Self:
        accumulated_items: int = sum(instance.databases_count() for instance in self.instances)
        if accumulated_items > UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT:
            raise ValueError(
                f'Current items count [{accumulated_items}] exceeds maximum number of items allowed [{UAP_SIA_DB_TARGETS_MAX_ITEMS_COUNT}]'
            )
        return self
