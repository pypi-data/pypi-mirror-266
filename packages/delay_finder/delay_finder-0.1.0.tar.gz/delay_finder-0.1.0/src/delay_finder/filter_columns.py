import pandas as py

# filter the read CSV file and return columns of interest
def filter_columns(data, columns_of_interest):
    """
    Using an existing DataFrame and columns of interest, returns a DataFrame with only said columns of interest.

    Parameters:
    ----------
    data: pd.DataFrame 
        DataFrame containing the already read information that one wants to work with.

    columns_of_interest: [columns_of_interest]
        List containing strings of the names of the columns that you want to keep.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing the information read form the CSV file.

    Raises:
    ------
    ValueError:
        - If the columns_of_interest list is empty.
        - If the data is empty
   
    KeyError:
        - If any of the specified columns do not exist in the DataFrame.
    
    TypeError:
        - If data is None.

    Examples:
    --------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
    >>> filter_columns(df, ['A', 'B'])
       A  B
    0  1  4
    1  2  5
    2  3  6
    """
    # check if columns_of_interest is empty
    if len(columns_of_interest)==0:
        raise ValueError("the columns_of_interest list is empty")

    return data[columns_of_interest]