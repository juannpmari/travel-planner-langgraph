# import json
import os

# import requests
import azure.functions as func

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from telegram import Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="message", methods=["POST", "GET"])
def telegram_webhook(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Received a request from Telegram')

    if req.method == 'POST':
        # Parse the incoming update from Telegram
        try:
            update = req.get_json()
            logger.info(f"Received update: {update}")

            # Process the update
            handle_update(update)

            # Respond with HTTP 200 OK
            return func.HttpResponse(status_code=200)
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return func.HttpResponse(status_code=500)
    else:
        # For webhook setup verification
        return func.HttpResponse("Hello, Telegram!", status_code=200)

def handle_update(update):
    # Check if the update has a message
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        message_text = message.get('text', '')

        # Process the message and get a response
        response_text = get_response(message_text,chat_id)

        # Send a message back to the user
        bot.send_message(chat_id=chat_id, text=response_text)


def get_response(message:str, chat_id:str):

    from agent_graph.graph import graph_factory, compile_workflow

    thread_id = chat_id #str(uuid.uuid4())
    config = {
        "configurable": {
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,
        }
    }
    builder = graph_factory()
    graph = compile_workflow(builder)
    
    
    logger.info("Getting response")
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

    for event in events:
        agent_response = str(event.get('messages')[-1].content)

    return agent_response