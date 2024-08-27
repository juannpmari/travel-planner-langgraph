from langchain_community.tools.tavily_search import TavilySearchResults


def get_web_searcher():
    """
    Creates and returns a web search tool using the TavilySearchResults API.

    This function initializes a TavilySearchResults instance with a maximum of 2 results
    per search query. The tool can be used to perform web searches and retrieve
    relevant information.

    Returns:
        TavilySearchResults: A configured web search tool instance.
    """
    tool = TavilySearchResults(max_results=2)
    return tool