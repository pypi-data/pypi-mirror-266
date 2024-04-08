from datetime import timedelta
from functools import cached_property
from os import getenv
from typing import Dict, List, Optional, Sequence, Set
from uuid import UUID

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from galileo_core.schemas.protect.payload import Payload
from galileo_core.schemas.protect.rule import Rule
from galileo_core.schemas.protect.ruleset import Ruleset


class Request(BaseModel):
    payload: Payload = Field(description="Payload to be processed.")
    project_id: Optional[UUID4] = Field(default=None, description="Project ID.", validate_default=True)
    stage_name: Optional[str] = Field(default=None, description="Stage name.", validate_default=True)
    stage_id: Optional[UUID4] = Field(default=None, description="Stage ID.", validate_default=True)
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

    @field_validator("project_id", mode="before")
    def project_id_from_env(cls, value: Optional[UUID4]) -> Optional[UUID4]:
        env_value = getenv("GALILEO_PROJECT_ID")
        if value is None and env_value:
            value = UUID(env_value)
        return value

    @field_validator("stage_name", mode="before")
    def stage_name_from_env(cls, value: Optional[str]) -> Optional[str]:
        env_value = getenv("GALILEO_STAGE_NAME")
        if value is None and env_value:
            value = env_value
        return value

    @field_validator("stage_id", mode="before")
    def stage_id_from_env(cls, value: Optional[UUID4]) -> Optional[UUID4]:
        env_value = getenv("GALILEO_STAGE_ID")
        if value is None and env_value:
            value = UUID(env_value)
        return value

    @model_validator(mode="after")
    def validate_stage(self) -> "Request":
        """
        Validate that either stage_id or both stage_name and project_id are provided.

        Returns
        -------
        Request
            The request object.

        Raises
        ------
        ValueError
            If neither stage_id nor both stage_name and project_id are provided.
        """
        if (self.stage_id) or (self.stage_name and self.project_id):
            return self
        else:
            raise ValueError("Either stage_id or both stage_name and project_id must be provided.")

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
