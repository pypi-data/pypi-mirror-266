from enum import Enum
from typing import Optional

from pydantic import BaseModel

from galileo_core.schemas.shared.metric import MetricValueType


class MetricComputationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    ERROR = "ERROR"


class MetricComputation(BaseModel):
    value: MetricValueType = None
    execution_time: Optional[float] = None
    status: Optional[MetricComputationStatus] = None
    error_message: Optional[str] = None
