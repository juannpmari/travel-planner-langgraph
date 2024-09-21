from langchain_core.tools import tool
    

@tool
def get_provider_data():
    """
    Call to get all the service providers offered by our company
    """
    providers = "Extreme Fishing, Pejerrey fishing, and others"
    return providers


#"We're Extreme Fishing, we offer guiding services in buenos aires, plesa call at +5498762345"