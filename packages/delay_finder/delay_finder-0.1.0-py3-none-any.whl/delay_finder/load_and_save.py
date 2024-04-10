import pandas as pd
import pickle

def load_data(file_path):
    """Load data from a CSV file.

    Parameters:
    ----------
    - file_path (str): The path to the CSV file containing the data.

    Returns:
    -------
    pandas.DataFrame: The loaded data as a DataFrame.

    Examples:
    --------
    >>> import pandas as pd
    >>> df = load_data('filename.csv') # Replace 'filename.csv' with your desired dataset filename
    """
    return pd.read_csv(file_path)

def save_model(model, file_path):
    """Save a trained model to a file using pickle.

    Parameters:
    ----------
    - model: The trained model object to be saved.
    - file_path (str): The path to save the model file.

    Returns:
    -------
    None

    Examples:
    --------
    >>> import pandas as pd
    >>> import pickle
    >>> from sklearn.dummy import DummyClassifier
    >>> dummy_classifier = DummyClassifier(strategy = "stratified", random_state = 12)
    >>> save_model(dummy_classifier)
    """
    with open(file_path, 'wb') as f:
        pickle.dump(model, f)
