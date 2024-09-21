from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from models.openai import get_openai
from tools.flow_tools import ToRecommendationsAssistant
from prompts.system_message import primary_assistant_system_message

def get_primary_assistant_runnable():
    
    llm = get_openai()

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                primary_assistant_system_message
            ),
            ("placeholder", "{messages}"),
        ]
    )

    primary_assistant_tools = [
        #TODO: add tool to call human
    ]

    assistant_runnable = primary_assistant_prompt | llm.bind_tools(
        primary_assistant_tools
        + [ToRecommendationsAssistant]
    )

    return assistant_runnable