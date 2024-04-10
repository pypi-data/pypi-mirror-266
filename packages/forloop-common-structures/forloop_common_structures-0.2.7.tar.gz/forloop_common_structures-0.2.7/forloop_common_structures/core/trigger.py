import datetime
from dataclasses import dataclass
from typing import Optional

from forloop_modules.queries.db_model_templates import TriggerFrequencyEnum


@dataclass
class Trigger:
    name: str
    first_run_date: datetime.datetime
    frequency: TriggerFrequencyEnum
    pipeline_uid: str
    project_uid: str
    uid: Optional[str] = None
