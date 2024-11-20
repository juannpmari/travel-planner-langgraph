from langchain_core.tools import tool

@tool
def get_acommodation_data():
    """
    Call to get data about acommodation services offered by our company
    """
    return "For Loreto, we've a 5 stars hotel at 100USD per night. we also have many hotels all over the world, just call us for updated information"