from langchain_core.tools import tool
from pydantic import BaseModel
import pandas as pd

acommodation_df = pd.read_csv('data/acommodation_data.csv')

@tool
def get_acommodation_data(query:str):
    """
    Call to get data about acommodation services offered by our company
    Args:
        query: pandas' dataframe formatted query, to filter acommodation data according to user needs. For example, query = "city in ['London','Paris']"
    """
    return str(acommodation_df.query(query).to_json())