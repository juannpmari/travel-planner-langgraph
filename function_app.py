import azure.functions as func
import logging
# import uuid
# # from llm_utils.utils import _print_event
import os

from dotenv import load_dotenv
load_dotenv('.env.dev')

os.environ["AZURE_CHAT_DEPLOYMENT_NAME"] = "gpt-4o-dev"

from agent_graph.graph import graph_factory, compile_workflow

builder = graph_factory()
graph = compile_workflow(builder)

thread_id = '4' #str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Update with the backup file so we can restart from the original place in each section


@app.route(route="message")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Welcome to the travel assistant')

    message = req.params.get('message')
    if not message:
        agent_response = f"Please pass a user message"



    # _printed = set()

    # while True:
    #     # Ask for user input dynamically
    #     question = input("Please enter your question (or type 'exit' to quit): ")
        
    #     if question.lower() == 'exit':
    #         break
    else:
        events = graph.stream(
            {"messages": ("user", message)}, config, stream_mode="values"
        )
        # for event in events:
        #     _print_event(event, _printed) #Doesn't print FunctionMessage's, only functioncallS (AIMessage's)
        snapshot = graph.get_state(config)
        # while snapshot.next:
        #         # The agent is trying to use a tool
        #         # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
        #         # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
            
        #     result = graph.invoke(
        #         None,
        #         config,
        #     )
        #     snapshot = graph.get_state(config)


    agent_response = str(snapshot.next) #result['messages'][-1].content
    return func.HttpResponse(agent_response)

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )