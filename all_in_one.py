# Primary assistant
from typing import Literal
from agents.assistant import Assistant, CompleteOrEscalate
from agents.primary_assistant import ToRecommendationsAssistant, get_primary_assistant_runnable
from agents.recommendations_assistant import get_recommendations_runnable
from langgraph.graph import StateGraph,END,START
from llm_utils.utils import create_tool_node_with_fallback
from states.states import State
from langgraph.prebuilt import tools_condition
from llm_utils.entry_node import create_entry_node
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from tools.web_searcher import get_web_searcher




builder = StateGraph(State)


#def user_info(state: State):
#   return {"user_info": ""}


#builder.add_node("fetch_user_info", user_info)
#builder.add_edge(START, "fetch_user_info")

builder.add_node( #dummy node to keep track of the current agent being used
    "enter_generate_recommendations",
    create_entry_node("Reccomendations Assistant", "generate_recommendations"),
)

builder.add_node("generate_recommendations", Assistant(get_recommendations_runnable()))
builder.add_edge("enter_generate_recommendations", "generate_recommendations")
builder.add_node(
    "generate_recommendations_tools",
    create_tool_node_with_fallback([get_web_searcher()]),
)



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


builder.add_edge( "generate_recommendations_tools","generate_recommendations")
builder.add_conditional_edges("generate_recommendations", route_generate_recommendations)


# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the main assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }

builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")

builder.add_node("primary_assistant", Assistant(get_primary_assistant_runnable()))
builder.add_node(
    "primary_assistant_tools", create_tool_node_with_fallback([]) #TODO: add primary assistant tools
)


def route_primary_assistant(
    state: State,
) -> Literal[
    "primary_assistant_tools",
    "enter_generate_recommendations"
    "__end__",
]:
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToRecommendationsAssistant.__name__:
            return "enter_generate_recommendations"
        return "primary_assistant_tools"
    raise ValueError("Invalid route")


# The assistant can route to one of the delegated assistants,
# directly use a tool, or directly respond to the user
builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    {
        "enter_generate_recommendations": "enter_generate_recommendations",
        "primary_assistant_tools": "primary_assistant_tools",
        END: END,
    },
)
builder.add_edge("primary_assistant_tools", "primary_assistant")


# Each delegated workflow can directly respond to the user
# When the user responds, we want to return to the currently active workflow
def route_to_workflow(
    state: State,
) -> Literal[
    "primary_assistant",
    "generate_recommendations"
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]


builder.add_conditional_edges(START, route_to_workflow)

# Compile graph

memory = MemorySaver()
part_4_graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[
        "generate_recommendations_tools"
    ],
)


from IPython.display import Image, display

try:
    mermaid_png = part_4_graph.get_graph(xray=True).draw_mermaid_png()
    with open('graph_visualization.png', 'wb') as f:
        f.write(mermaid_png)
    display(Image('graph_visualization.png'))
except Exception:
    # This requires some extra dependencies and is optional
    pass