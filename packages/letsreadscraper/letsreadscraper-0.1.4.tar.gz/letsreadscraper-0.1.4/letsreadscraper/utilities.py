import pandas

def xlookup(lookup_value, lookup_array, return_array, if_not_found:str = ''):
    """Replicate xlookup in Python using the pandas library

    Args:
        lookup_value (str): the value we are interested, this will be a string value
        lookup_array (_type_): this is a column inside the source pandas dataframe, we are looking for the “lookup_value” inside this array/column
        return_array (_type_): this is a column inside the source pandas dataframe, we want to return values from this column
        if_not_found (str, optional): will be returned if the “lookup_value” is not found. Defaults to ''.

    Returns:
        _type_: Returns the matched value
    """    
    match_value = return_array.loc[lookup_array == lookup_value]
    if match_value.empty:
        return f'"{lookup_value}" not found!' if if_not_found == '' else if_not_found

    else:
        return match_value.tolist()[0]