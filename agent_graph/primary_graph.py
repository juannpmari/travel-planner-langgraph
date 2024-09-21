# Primary assistant
from typing import Literal
from agents.assistant import Assistant
from agents.primary_assistant import ToRecommendationsAssistant, get_primary_assistant_runnable
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

    return builder

    

# Compile graph

#memory = MemorySaver()
#part_4_graph = builder.compile(
 #   checkpointer=memory,
    # Let the user approve or deny the use of sensitive tools
  #  interrupt_before=[
  #      "update_flight_sensitive_tools",
  #      "book_car_rental_sensitive_tools",
  #      "book_hotel_sensitive_tools",
  #      "book_excursion_sensitive_tools",
  #  ],
#)