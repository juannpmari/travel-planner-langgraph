from langchain_core.prompts import ChatPromptTemplate
from models.openai import get_openai
from tools.recommendation_tools.web_searcher import get_web_searcher
from tools.flow_tools import CompleteOrEscalate
from prompts.system_message import recommendations_assistant_system_message

def get_recommendations_runnable():
    recommendation_generator_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                recommendations_assistant_system_message,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_openai()

    generate_recommendations_tools = [get_web_searcher()]
    generate_recommendations_runnable = recommendation_generator_prompt | llm.bind_tools( #TODO: check .bind_tools vs llm-invoke(functions=...)
        generate_recommendations_tools + [CompleteOrEscalate]
    )
    return generate_recommendations_runnable
