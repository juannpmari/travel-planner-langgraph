from langchain_openai import AzureChatOpenAI
import os
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME")



def get_openai():
    llm = AzureChatOpenAI(
    openai_api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_CHAT_DEPLOYMENT_NAME,
    openai_api_version="2024-02-15-preview",
    temperature=0.25,
    request_timeout=550,
    max_tokens=2000,
    )
    return llm