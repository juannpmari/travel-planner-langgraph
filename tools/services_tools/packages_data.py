from langchain_core.tools import tool
    

@tool
def get_packages_data():
    """
    Call to get all the travel packages offered by our company
    """
    packages = "3 week trip to Egipt, with Hotel and flights included, USD 3000"
    return packages