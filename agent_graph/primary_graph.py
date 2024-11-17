# Primary assistant
from typing import Literal
from agent_graph.common import pop_dialog_state
from agents.assistant import Assistant
from agents.primary_assistant import ToRecommendationsAssistant, ToServicesAssistant, get_primary_assistant_runnable
from langgraph.graph import StateGraph,END,START
from llm_utils.utils import create_tool_node_with_fallback
from states.state import State
from langgraph.prebuilt import tools_condition



def create_primary_graph():

    builder = StateGraph(State)

    builder.add_node("primary_assistant", Assistant(get_primary_assistant_runnable()))
    builder.add_node(
        "primary_assistant_tools", create_tool_node_with_fallback([]) #TODO: add primary assistant tools
    )


    def route_primary_assistant(
        state: State,
    ) -> Literal[
        "primary_assistant_tools",
        "enter_generate_recommendations",
        "enter_services_assistant",
        "__end__", #END
    ]:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            if tool_calls[0]["name"] == ToRecommendationsAssistant.__name__:
                return "enter_generate_recommendations"
            if tool_calls[0]["name"] == ToServicesAssistant.__name__:
                return "enter_services_assistant"
            return "primary_assistant_tools"
        raise ValueError("Invalid route")


    # The assistant can route to one of the delegated assistants,
    # directly use a tool, or directly respond to the user
    builder.add_conditional_edges(
        "primary_assistant",
        route_primary_assistant,
        {
            "primary_assistant_tools": "primary_assistant_tools",
            "enter_generate_recommendations": "enter_generate_recommendations",
            "enter_services_assistant":"enter_services_assistant",
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
        "generate_recommendations",
        "services_assistant",
        "accomodation_assistant"
    ]:
        """If we are in a delegated state, route directly to the appropriate assistant."""
        dialog_state = state.get("dialog_state") #TODO: Get dialog_states from enum
        if not dialog_state:
            return "primary_assistant"
        return dialog_state[-1]

    builder.add_conditional_edges(START, route_to_workflow)

    
    builder.add_node("leave_skill", pop_dialog_state)
    builder.add_edge("leave_skill", "primary_assistant")

    return builder