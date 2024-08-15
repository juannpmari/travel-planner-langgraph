from pydantic import BaseModel


class RequestAssistance(BaseModel):
    """Escalate the conversation to the user. Use this if you need extra information about the user in order to create a customized answer to his query.

    To use this function, relay the user's 'request' so the expert can provide the right guidance.
    """

    request: str

def get_human_help():
    return RequestAssistance