import requests
from rich import print
import pandas as pd
import jsons
import os
import letsreadscraper as lrs

def scrape_language_details():
    """ Gets all the Language details:

    Returns:
        DataFrame: Returns a dataframe with all Language details from Let's Read Website!
    """    
    response = requests.get('https://letsreadasia.org/api/language')
    results = [item for item in response.json()]

    df = pd.json_normalize(results).sort_values(by=['country'])
    df['name'] = df['name'].str.lower()
    return df

def scrape_by_language(language, limit=10):
    """_summary_

    Args:
        language (str): Enter the language of the books that you are interested to gather information about
        limit (int, optional): Enter number of books to gather information

    Returns:
        DataFrame: Returns a dataframe with book details based on the parameters provided
    """    
    df_language = scrape_language_details()
    language_value = language
    lId_value = lrs.utilities.xlookup(lookup_value=language_value, lookup_array=df_language["name"], return_array=df_language["id"])
    limit_value = int(limit)

    params = {
    'searchText': '',
    'lId': lId_value,
    'readingLevel': '',
    'countryOfOrigin': '',
    'audio': 'false',
    #'cursorWebSafeString': '1',
    'limit': limit_value,
    }
    
    response = requests.get('https://letsreadasia.org/api/book/elastic/search/', params=params)

    results = [item for item in response.json()["other"]]

    df = pd.json_normalize(results)
    return df