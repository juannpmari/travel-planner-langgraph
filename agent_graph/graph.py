from agent_graph.primary_graph import create_primary_graph
from agent_graph.recommendations_graph import create_recommendations_subgraph
from agent_graph.services_graph import create_services_subgraph
from langgraph.checkpoint.memory import MemorySaver


def graph_factory():
    #TODO: improve this logic
    builder = create_primary_graph()
    builder = create_recommendations_subgraph(builder)
    builder = create_services_subgraph(builder)
    return builder


def compile_workflow(builder):
    
    memory = MemorySaver()

    graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[
        "generate_recommendations_tools"
    ],
    )

    return graph
