from dotenv import load_dotenv
load_dotenv('.env')

from agent_graph.graph import compile_graph, create_graph

graph = create_graph()
workflow = compile_graph(graph)

query = {'messages':'Hi! what is your name?'}
result = workflow.invoke(query)