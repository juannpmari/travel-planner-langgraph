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

from tools.services_tools.packages_data import get_packages_data


# Subgraph correponding to the services assistant

def create_accomodation_subgraph(builder):
    builder.add_node( #dummy node to keep track of the current agent being used
        "enter_accomodation_assistant",
        create_entry_node("Accomodation Assistant", "accomodation_assistant"),
    )

    builder.add_node("accomodation_assistant", Assistant(get_services_runnable()))
    builder.add_edge("enter_accomodation_assistant", "accomodation_assistant")
    builder.add_node(
        "accomodation_assistant_tools",
        create_tool_node_with_fallback([get_packages_data]),
    )

    def route_accomodation_services(
        state: State,
    ) -> Literal[
        "accomodation_assistant_tools",
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
        return "accomodation_assistant_tools"
    

    builder.add_edge("accomodation_assistant_tools", "accomodation_assistant")
    builder.add_conditional_edges("accomodation_assistant", route_accomodation_services)
   
    return builder
