from langchain_core.tools import tool
import pandas as pd

packages_df = pd.read_csv('data/packages_data.csv')

@tool
def get_packages_data(query:str):
    """
    Call to get all the travel packages offered by our company
    Args:
        query: pandas' dataframe formatted query, to filter packages data according to user needs. For example, query = "city in ['London','Paris']"
   
    """
    return str(packages_df.query(query).to_json())