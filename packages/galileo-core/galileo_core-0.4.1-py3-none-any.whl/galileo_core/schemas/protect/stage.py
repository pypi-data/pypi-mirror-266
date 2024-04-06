from typing import Optional

from pydantic import UUID4, BaseModel, Field, ValidationInfo, field_validator

from galileo_core.schemas.protect.action import Action


class Stage(BaseModel):
    name: str = Field(description="Name of the stage. Must be unique within the project.")
    project_id: UUID4 = Field(description="ID of the project to which this stage belongs.")
    description: Optional[str] = Field(
        description="Optional human-readable description of the goals of this guardrail.", default=None
    )
    action: Optional[Action] = Field(
        description="An optional action (kill switch) to take that supersedes all ruleset validations.", default=None
    )
    action_enabled: bool = Field(
        description="Whether the action is enabled. If False, the action will not be applied.", default=False
    )

    @field_validator("action_enabled", mode="before")
    def validate_action_enabled(cls, value: bool, info: ValidationInfo) -> bool:
        if value and info.data.get("action") is None:
            raise ValueError("Action cannot be enabled if action is not set.")
        return value
