from datetime import timedelta
from functools import cached_property
from typing import Dict, List, Optional, Sequence, Set

from pydantic import UUID4, BaseModel, ConfigDict, Field, computed_field

from galileo_core.schemas.protect.payload import Payload
from galileo_core.schemas.protect.rule import Rule
from galileo_core.schemas.protect.ruleset import Ruleset


class Request(BaseModel):
    project_id: UUID4
    payload: Payload = Field(description="Payload to be processed.")
    rulesets: Sequence[Ruleset] = Field(
        default_factory=list,
        description="Rulesets to be applied to the payload.",
        validation_alias="prioritized_rulesets",
    )
    timeout: float = Field(
        default=timedelta(minutes=5).total_seconds(),
        description="Optional timeout for the guardrail execution in seconds. This is not the timeout for the request. If not set, a default timeout of 5 minutes will be used.",
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional additional metadata. This will be echoed back in the response.",
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional additional HTTP headers that should be included in the response.",
    )

    model_config = ConfigDict(populate_by_name=True)

    # https://github.com/python/mypy/issues/1362
    @computed_field  # type: ignore[misc]
    @cached_property
    def rules(self) -> List[Rule]:
        rules: List[Rule] = []
        for ruleset in self.rulesets:
            rules.extend(ruleset.rules)
        return rules

    # https://github.com/python/mypy/issues/1362
    @computed_field  # type: ignore[misc]
    @cached_property
    def metrics(self) -> Set[str]:
        metrics_to_compute = []
        for rule in self.rules:
            metrics_to_compute.append(rule.metric)
        return set(metrics_to_compute)

    # https://github.com/python/mypy/issues/1362
    @computed_field  # type: ignore[misc]
    @cached_property
    def timeout_ns(self) -> float:
        return self.timeout * 1e9
