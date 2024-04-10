import pandas as pd

# read CSV file and make a DataFrame
def read(file_name):
    """
    Using the relative path, reads the file and returns a data frame of said data.

    Parameters:
    ----------
    file_name: string containing the relative path to a CSV file that will be read.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing the information read form the CSV file.

    Raises:
    ------
    FileNotFoundError:
        - If the file does not exist.
    
    pd.errors.EmptyDataError:
        - If the file is empty.
    
    Examples:
    --------
    >>> import pandas as pd
    >>> import altair as alt
    >>> df = read(filename) *replace filename with the name of the file and its relative path
    >>> df.print
    
    """
    return pd.read_csv(file_name)