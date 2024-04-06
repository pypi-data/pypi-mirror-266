from typing import Optional, Sequence

from pydantic import BaseModel, Field, field_validator

from galileo_core.schemas.protect.action import Action, BaseAction, PassthroughAction
from galileo_core.schemas.protect.rule import Rule


class Ruleset(BaseModel):
    rules: Sequence[Rule] = Field(
        description="List of rules to evaluate. Atleast 1 rule is required.", default_factory=list, min_length=1
    )
    action: Action = Field(description="Action to take if all the rules are met.", default_factory=PassthroughAction)
    description: Optional[str] = Field(description="Description of the ruleset.", default=None)
    timeout: Optional[int] = Field(
        description="Time in nano-seconds for all the rules to be evaluated. If not provided, will evaluate all the rules to completion.",
        default=None,
    )

    @field_validator("action", mode="before")
    def validate_action(cls, value: Optional[BaseAction]) -> BaseAction:
        if not value:
            value = PassthroughAction()
        return value
