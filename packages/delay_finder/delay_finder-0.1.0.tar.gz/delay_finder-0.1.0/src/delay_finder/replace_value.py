import pandas as pd

def replace_value(dataframe, column, old_value, new_value):
    """
    Replaces a value in a column with a new value in a pandas DataFrame.
    Returns a pandas DataFrame.

    Parameters:
    ----------
    dataframe : pandas.DataFrame
                The dataframe with the data.
    column : str
             The column in which a value is to be changed.
    old_value : str, int, or float
                The value that will be replaced.
    new_value : str, int, or float
                The value that is the replacement.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with a new specified value, that replaced the old specified value,
        in the specified column

    Raises:
    ------
    TypeError
        If the input argument for:
        - dataframe is not of type pandas.DataFrame
        - column is not of type str
        - old_value is not of type str, int, or float
        - new_value is not of type str, int, or float  
    Exception
        If the input argument 
        - column is not in the inputted pandas Dataframe
        - old_value is not in the specified column
    
    Examples:
    --------
    >>> import pandas as pd
    >>> df = pd.read_csv('filename.csv') # Replace 'filename.csv' with your desired dataset filename
    >>> result = replace_value(df, column_name, "old value", "new value")
    >>> print(result)

    """
    # check if the inputs are the correct type
    if type(dataframe) is not pd.DataFrame:
        raise TypeError("You are not using a pandas DataFrame for the dataframe input")
    if type(column) is not str:
        raise TypeError("You are not using a string for the column input")
    if type(old_value) not in [str, int, float]:
        raise TypeError("You are not using a string, integer, or float for the old_value input")
    if type(new_value) not in [str, int, float]:
        raise TypeError("YYou are not using a string, integer, or float for the new_value input")
    
    # check if the specifed column is in the inputted pandas DataFrame
    if column not in dataframe.columns:
        raise Exception("The specified column is not in the specified dataframe")

    # check if old_value is in the specified column
    if old_value not in dataframe[column].values:
        raise Exception("The specified old_value is not in the specified column")

    dataframe.loc[dataframe[column] == old_value, column] = new_value
    return dataframe