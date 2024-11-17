import os
from agent_graph.primary_graph import create_primary_graph
from agent_graph.recommendations_graph import create_recommendations_subgraph
from agent_graph.services_accomodation_graph import create_accomodation_subgraph
from agent_graph.services_graph import create_services_subgraph
# from langgraph.checkpoint.memory import MemorySaver

from states.mongo_checkpointer import MongoDBSaver


def graph_factory():
    #TODO: improve this logic
    builder = create_primary_graph()
    builder = create_recommendations_subgraph(builder)
    builder = create_services_subgraph(builder)
    builder = create_accomodation_subgraph(builder)
    return builder


def compile_workflow(builder):
    
    # memory = MemorySaver()
    # graph = builder.compile(
    #     checkpointer=memory,
    #     # interrupt_before=[ #TODO: check if this is necessary
    #     #     "generate_recommendations_tools",
    #     #     "services_assistant_tools"
    #     # ],
    # )
    

    mongo_checkpointer =  MongoDBSaver.from_conn_info(connection_str=os.getenv('MONGO_CHECKPOINTERR_CONN_STR'))
    graph = builder.compile(checkpointer=mongo_checkpointer)

    return graph
