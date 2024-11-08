from enum import Enum
from typing import Annotated, Literal, Optional

from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[ #To keep track of the current agent being used
        list[
            Literal[
                "primary_assistant", #primary assistant
                "generate_recommendations", #recommendations assistant,
                "services_assistant",
                "accomodation_assistant"
            ]
        ],
        update_dialog_stack,
    ]


class DialogStateEnum(Enum): #TODO: complete this
    PRIMARY_ASSISTANT = "primary_assistant"