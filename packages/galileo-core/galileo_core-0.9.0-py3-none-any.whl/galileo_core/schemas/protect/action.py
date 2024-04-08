from enum import Enum
from random import choice
from typing import Literal, Sequence, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class ActionType(str, Enum):
    OVERRIDE = "OVERRIDE"
    PASSTHROUGH = "PASSTHROUGH"


class ActionResult(BaseModel):
    type: ActionType = Field(description="Type of action that was taken.")
    value: str = Field(description="Value of the action that was taken.")


class BaseAction(BaseModel):
    type: ActionType = Field(description="Type of action to take.")

    def apply(self, response: str) -> ActionResult:
        raise NotImplementedError


class OverrideAction(BaseAction):
    type: Literal[ActionType.OVERRIDE] = ActionType.OVERRIDE
    choices: Sequence[str] = Field(
        description="List of choices to override the response with. If there are multiple choices, one will be chosen at random when applying this action.",
        min_length=1,
    )

    def apply(self, response: str) -> ActionResult:
        return ActionResult(type=self.type, value=choice(self.choices))


class PassthroughAction(BaseAction):
    type: Literal[ActionType.PASSTHROUGH] = ActionType.PASSTHROUGH

    def apply(self, response: str) -> ActionResult:
        return ActionResult(type=self.type, value=response)


Action = Annotated[Union[OverrideAction, PassthroughAction], Field(discriminator="type")]
