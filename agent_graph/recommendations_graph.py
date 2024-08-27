from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

builder = StateGraph(State)


def user_info(state: State):
    return {"user_info": ""}


builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")

builder.add_node(
    "enter_generate_recommendations",
    create_entry_node("Reccomendations Assistant", "generate_recommendations"),
)
builder.add_node("generate_recommendations", Assistant(generate_recommendations_runnable))
builder.add_edge("enter_generate_recommendations", "generate_recommendations")

def route_generate_recommendations(
    state: State,
) -> Literal[
    "generate_recommendations_tools",
    "leave_skill",
    "__end__",
]:
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    #safe_toolnames = [t.name for t in update_flight_safe_tools]
    #if all(tc["name"] in safe_toolnames for tc in tool_calls):
    #   return "update_flight_safe_tools"
    return "generate_recommendations_tools"


builder.add_edge("generate_recommendations_tools", "generate_recommendations")
builder.add_conditional_edges("generate_recommendations", route_generate_recommendations)

builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")