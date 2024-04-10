from typing import Optional

from pydantic import UUID4, BaseModel, Field

from galileo_core.schemas.protect.action import Action, PassthroughAction


class Stage(BaseModel):
    name: str = Field(description="Name of the stage. Must be unique within the project.")
    project_id: UUID4 = Field(description="ID of the project to which this stage belongs.")
    description: Optional[str] = Field(
        description="Optional human-readable description of the goals of this guardrail.", default=None
    )
    action: Action = Field(
        default_factory=PassthroughAction,
        description="An optional action (kill switch) to take that supersedes all ruleset validations.",
    )
    action_enabled: bool = Field(
        description="Whether the action is enabled. If False, the action will not be applied.", default=False
    )
