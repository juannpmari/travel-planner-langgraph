import json
import os

import requests
import azure.functions as func

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)



app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="message")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Welcome to the travel assistant')

    # Check if the request is a GET request for verification
    if req.method == 'GET':
        logger.info("got GET request")
        mode = req.params.get('hub.mode')
        token = req.params.get('hub.verify_token')
        challenge = req.params.get('hub.challenge')

        # Replace 'your_verify_token' with the token you've set up in the Meta Developer settings
        if mode == 'subscribe' and token == '123456':
            # Respond with the challenge to verify the webhook
            return func.HttpResponse(challenge, status_code=200)
        else:
            # If token doesn't match or other issues, return a 403 Forbidden response
            return func.HttpResponse('Verification token mismatch', status_code=403)

    # Handle POST requests here (i.e., messages from WhatsApp)
    if req.method == 'POST':
        logger.info("got POST request")
        logger.info("printing json")
        logger.info(req.get_json())

        # # Parse the incoming message from WhatsApp
        req_body = req.get_json()
        message = req_body['entry'][0]['changes'][0]['value']['messages'][0]
        message_body = message['text']['body']
        
        try:
            lgph_response = get_response(message_body)
        except Exception as e:
            logger.info(f"Error {e}")
            response_payload = {
                "message":f"Error {e}"
            }
            return func.HttpResponse(json.dumps(response_payload), mimetype="application/json", status_code=500)
  
        data = get_text_message_input(
            recipient=os.getenv('RECIPIENT_WAID'), text = lgph_response
        )

        wpp_response = send_message(data)

        response_payload = {
            "recipient_type": "individual",
            "to": message['from'],
            "type": "text",
            "text": {
                "body": wpp_response.json()
            }
        }

        logger.info(f"Sending response: {response_payload}")

        return func.HttpResponse(json.dumps(response_payload), mimetype="application/json", status_code=200)


def get_response(message):

    from agent_graph.graph import graph_factory, compile_workflow

    thread_id = '1' #str(uuid.uuid4())
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


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
    }

    url = f"https://graph.facebook.com/{os.getenv('VERSION')}/{os.getenv('PHONE_NUMBER_ID')}/messages"

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
        return response
    else:
        print(response.status_code)
        print(response.text)
        return response