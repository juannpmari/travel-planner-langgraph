from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,END
from langgraph.prebuilt import tools_condition
from agent_graph.common import pop_dialog_state
from agents.services_assistant import get_services_runnable
from agents.assistant import Assistant
from llm_utils.utils import create_tool_node_with_fallback
from tools.flow_tools import CompleteOrEscalate
from llm_utils.entry_node import create_entry_node
from states.state import State    

from tools.recommendation_tools.providers_data import get_provider_data


# Subgraph correponding to the services assistant

def create_services_subgraph(builder):
    builder.add_node( #dummy node to keep track of the current agent being used
        "enter_services_assistant",
        create_entry_node("Services Assistant", "services_assistant"),
    )

    builder.add_node("services_assistant", Assistant(get_services_runnable()))
    builder.add_edge("enter_services_assistant", "services_assistant")
    builder.add_node(
        "services_assistant_tools",
        create_tool_node_with_fallback([get_provider_data]),
    )

    def route_retrieve_services(
        state: State,
    ) -> Literal[
        "services_assistant_tools",
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
        return "services_assistant_tools"
    

    builder.add_edge("services_assistant_tools", "services_assistant")
    builder.add_conditional_edges("services_assistant", route_retrieve_services)

    
    # builder.add_node("leave_skill", pop_dialog_state)
    # builder.add_edge("leave_skill", "primary_assistant")

    return builder
