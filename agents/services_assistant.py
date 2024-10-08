from langchain_core.prompts import ChatPromptTemplate
from models.openai import get_openai
# from tools.recommendation_tools.web_searcher import get_web_searcher
from tools.services_tools.packages_data import get_packages_data
from tools.flow_tools import ToAccomodationAssistant, CompleteOrEscalate
from prompts.system_message import services_assistant_system_message

def get_services_runnable():
    recommendation_generator_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                services_assistant_system_message,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_openai()

    services_assistant_tools = [get_packages_data]
    services_assistant_tools_runnable = recommendation_generator_prompt | llm.bind_tools(
        services_assistant_tools + [ToAccomodationAssistant, CompleteOrEscalate]
    )
    return services_assistant_tools_runnable
