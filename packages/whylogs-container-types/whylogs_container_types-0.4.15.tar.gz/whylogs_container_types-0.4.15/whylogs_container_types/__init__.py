from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

from langkit.core.metric import MetricCreator
from langkit.core.validation import Validator
from langkit.core.workflow import Callback
from whylogs.core.schema import DatasetSchema


class DatasetCadence(Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"


class DatasetUploadCadenceGranularity(Enum):
    MINUTE = "M"
    HOUR = "H"
    DAY = "D"


@dataclass(frozen=True)
class DatasetUploadCadence:
    interval: int
    granularity: DatasetUploadCadenceGranularity


@dataclass(frozen=True)
class DatasetOptions:
    dataset_cadence: DatasetCadence
    whylabs_upload_cadence: DatasetUploadCadence
    schema: Optional[DatasetSchema] = None


@dataclass(frozen=True)
class LangkitOptions:
    metrics: List[MetricCreator] = field(default_factory=list)
    callbacks: List[Callback] = field(default_factory=list)
    validators: List[Validator] = field(default_factory=list)


DatasetId = str


@dataclass(frozen=True)
class ContainerConfiguration:
    langkit_config: Dict[DatasetId, LangkitOptions] = field(default_factory=dict)
    whylogs_config: Dict[DatasetId, DatasetOptions] = field(default_factory=dict)


ContainerConfigFn = Callable[[], ContainerConfiguration]
