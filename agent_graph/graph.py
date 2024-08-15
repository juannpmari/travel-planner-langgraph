from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode,tools_condition
from models.openai import get_openai
from prompts.system_message import system_message
from states.states import State
from tools.human_help import get_human_help
from tools.web_searcher import get_web_searcher
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import ToolMessage,AIMessage,SystemMessage, HumanMessage

system_message_str = system_message

llm = get_openai()

web_searcher_tool = get_web_searcher()
human_help_tool = get_human_help()
llm_with_tools = llm.bind_tools([web_searcher_tool,human_help_tool])

#TODO: debería ir en una clase Agent como en el ejemplo de websearch
def recommender(state: State):
    # SYSTEM_MESSAGE = SystemMessage(content=system_message_str)
    response = llm_with_tools.invoke((state["messages"]))  #TODO: implement wrapper run_llm (ver passabot)
    ask_human = False
    if (
        response.tool_calls
        and response.tool_calls[0]["name"] == human_help_tool.__name__
    ):
        ask_human = True
    return {"messages": [response], "ask_human": ask_human}


def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )

def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(
            create_response("No response from human.", state["messages"][-1])
        )
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }

def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    # Otherwise, we can route as before
    return tools_condition(state)


def create_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("recommender",recommender)
    graph_builder.add_node("tools",ToolNode(tools=[web_searcher_tool]))

    graph_builder.add_node("human", human_node)


    # graph_builder.add_conditional_edges(
    #     "recommender",
    #     tools_condition,
    # )
    graph_builder.add_conditional_edges(
    "recommender",
    select_next_node,
    {"human": "human", "tools": "tools", "__end__": "__end__"},
)

    graph_builder.add_edge("tools", "recommender") #si o si debe llamarse tools?
    graph_builder.add_edge("human", "recommender")

    graph_builder.set_entry_point("recommender")

    return graph_builder


def compile_graph(graph):
    return graph.compile()


