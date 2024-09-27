from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,END
from langgraph.prebuilt import tools_condition
from agent_graph.common import pop_dialog_state
from agents.recommendations_assistant import get_recommendations_runnable
from agents.assistant import Assistant
from llm_utils.utils import create_tool_node_with_fallback
from tools.flow_tools import CompleteOrEscalate
from llm_utils.entry_node import create_entry_node
from states.state import State    

from tools.recommendation_tools.web_searcher import get_web_searcher


# Subgraph correponding to the recommendations assistant

def create_recommendations_subgraph(builder):
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
        return "generate_recommendations_tools"


    builder.add_edge("generate_recommendations_tools", "generate_recommendations")
    builder.add_conditional_edges("generate_recommendations", route_generate_recommendations)


    # # This node will be shared for exiting all specialized assistants
    # def pop_dialog_state(state: State) -> dict:
    #     """Pop the dialog stack and return to the main assistant.

    #     This lets the full graph explicitly track the dialog flow and delegate control
    #     to specific sub-graphs.
    #     """
    #     messages = []
    #     if state["messages"][-1].tool_calls:
    #         # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
    #         messages.append(
    #             FunctionMessage(
    #                 content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
    #                 tool_call_id=state["messages"][-1].tool_calls[0]["id"],
    #             )
    #         )
    #     return {
    #         "dialog_state": "pop",
    #         "messages": messages,
    #     }


    return builder