from langchain_community.tools.tavily_search import TavilySearchResults


def get_web_searcher():
    tool = TavilySearchResults(max_results=2)
    return tool