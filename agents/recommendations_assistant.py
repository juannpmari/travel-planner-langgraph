#from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from models.openai import get_openai
from states.states import State
from tools.web_searcher import get_web_searcher
from agents.assistant import CompleteOrEscalate


def get_recommendations_runnable():
    recommendation_generator_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a specialized assistant for handling flight updates. "
                "The primary assistant delegates work to you whenever the user needs help getting recommendations for their trip. "
                "\n\nIf the user needs help, and none of your tools are appropriate for it, then"
                ' "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.',
            ),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_openai()

    generate_recommendations_tools = [get_web_searcher()]
    generate_recommendations_runnable = recommendation_generator_prompt | llm.bind_tools(
        generate_recommendations_tools + [CompleteOrEscalate]
    )
    return generate_recommendations_runnable
