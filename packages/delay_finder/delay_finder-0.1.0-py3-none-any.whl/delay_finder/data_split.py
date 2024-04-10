import pandas as pd
from sklearn.model_selection import train_test_split

def data_split(data, train_file_name, test_file_name):
    """
    Split the input DataFrame into train and test sets, and then save them into CSV files.

    Parameters:
    ----------
    data : pd.DataFrame
        Input DataFrame to be split.
        
    train_file_name : str
        Name of the CSV file to be saved to the train set.
        
    test_file_name : str
        Name of the CSV file to be saved to the test set.

    Returns:
    -------
    None

    Raises:
    ------
    TypeError:
        If the input data is not a DataFrame.
    ValueError:
        If either of the file names is empty.

    Examples:
    --------
    >>> data_split(input_data, 'train_data.csv', 'test_data.csv')
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")
    if not train_file_name or not test_file_name:
        raise ValueError("File names cannot be empty.")

    # Split the data into train and test sets
    train, test = train_test_split(data, test_size=0.2, random_state=12)

    # Save the train and test sets into CSV files
    train.to_csv(train_file_name, index=False)
    test.to_csv(test_file_name, index=False)