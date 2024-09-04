from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from models.openai import get_openai


class ToRecommendationsAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle generating recommendations for the user's trip."""

    request: str = Field(
        description="Any necessary followup questions the recommendations assistant should clarify before proceeding."
    )


def get_primary_assistant_runnable():
    
    llm = get_openai()

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful customer support assistant for Swiss Airlines. "
                "Your primary role is to search for flight information and company policies to answer customer queries. "
                "If a customer requests to update or cancel a flight, book a car rental, book a hotel, or get trip recommendations, "
                "delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You are not able to make these types of changes yourself."
                " Only the specialized assistants are given permission to do this for the user."
                "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
                "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
                " When searching, be persistent. Expand your query bounds if the first search returns no results. "
                " If a search comes up empty, expand your search before giving up."
            ),
            ("placeholder", "{messages}"),
        ]
    )

    primary_assistant_tools = [
        #get_web_searcher(),
        #search_flights,
        #lookup_policy,
    ]

    assistant_runnable = primary_assistant_prompt | llm.bind_tools(
        primary_assistant_tools
        + [ToRecommendationsAssistant]
    )

    return assistant_runnable