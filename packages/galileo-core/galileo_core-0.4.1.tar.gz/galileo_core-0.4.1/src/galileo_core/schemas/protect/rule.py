from enum import Enum
from typing import Union

from pydantic import BaseModel, Field

from galileo_core.schemas.shared.metric import MetricValueType


class RuleOperator(str, Enum):
    gt = "gt"
    lt = "lt"
    gte = "gte"
    lte = "lte"
    eq = "eq"
    neq = "neq"
    contains = "contains"


class Rule(BaseModel):
    metric: str = Field(description="Name of the metric.")
    operator: RuleOperator = Field(description="Operator to use for comparison.")
    target_value: Union[str, float, int] = Field(description="Value to compare with for this metric (right hand side).")

    def evaluate(self, value: MetricValueType) -> bool:
        if value is not None:
            if isinstance(value, (float, int)) and isinstance(self.target_value, (float, int)):
                if self.operator == RuleOperator.gt:
                    return value > self.target_value
                elif self.operator == RuleOperator.lt:
                    return value < self.target_value
                elif self.operator == RuleOperator.gte:
                    return value >= self.target_value
                elif self.operator == RuleOperator.lte:
                    return value <= self.target_value
                elif self.operator == RuleOperator.eq:
                    return value == self.target_value
                elif self.operator == RuleOperator.neq:
                    return value != self.target_value
            elif isinstance(value, str) and isinstance(self.target_value, str):
                if self.operator == RuleOperator.eq:
                    return value == self.target_value
                elif self.operator == RuleOperator.neq:
                    return value != self.target_value
            elif isinstance(value, list) and isinstance(self.target_value, str):
                if self.operator == RuleOperator.contains:
                    return self.target_value in value
        return False
