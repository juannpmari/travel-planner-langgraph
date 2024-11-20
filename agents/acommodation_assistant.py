from langchain_core.prompts import ChatPromptTemplate
from models.openai import get_openai
# from tools.recommendation_tools.web_searcher import get_web_searcher
from tools.services_tools.acommodation_data import get_acommodation_data
from tools.flow_tools import CompleteOrEscalate
from prompts.system_message import accomodation_assistant_system_message

def get_acommodation_runnable():
    acommodation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                accomodation_assistant_system_message,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_openai()

    acommodation_assistant_tools = [get_acommodation_data]
    acommodation_assistant_tools_runnable = acommodation_prompt | llm.bind_tools(
        acommodation_assistant_tools + [CompleteOrEscalate]
    )
    return acommodation_assistant_tools_runnable
