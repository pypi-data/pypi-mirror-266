import pandas as pd
import altair as alt

# make histograms for the numeric columns
def make_histogram(data, column: str, x_title: str, w=250, h=150):
    """ Using the data, column of interest, title, and proportion, returns a histogram.

    Parameters:
    ----------
    dataframe : pandas.DataFrame
                The dataframe with the data that will be used to make the histogram.
    column : str
             The column of the dataframe that will be on the x-axis of the resulting histogram.
    x_title : str
              The x-axis title of the resulting histogram.
    w : int, optional
        The width (in pixels) of the resulting histogram (the default is 250).
    h : int, optional
        The height (in pixels) of the resulting histogram (the default is 150).

    Returns:
    -------
    altair.vegalite.v5.api.Chart
        An altair histogram with the specified column on the x-axis and
        number of flights on the y-axis.

    Raises:
    ------
    TypeError
        If the input argument for:
        - data is not of type pandas.DataFrame
        - column is not of type str
        - w is not of type int
        - h is not of type int
    Exception
        If the input argument 
        - column is not in the inputted pandas Dataframe
    
    Examples:
    --------
    >>> import pandas as pd
    >>> import altair as alt
    >>> df = pd.read_csv('filename.csv') # Replace 'filename.csv' with your desired dataset filename
    >>> result = make_histogram(df, column_name, "x-axis title", w=200, h=200)
    >>> result

    """
    # check if the inputs are the correct type
    if type(data) is not pd.DataFrame:
        raise TypeError("You are not using a pandas DataFrame for the dataframe input")
    if type(column) is not str:
        raise TypeError("You are not using a string for the column input")
    if type(w) is not int:
        raise TypeError("You are not using an integer for the width (w) input")
    if type(h) is not int:
        raise TypeError("You are not using an integer for the height (h) input")
    
    # check if the specifed column is in the inputted pandas DataFrame
    if column not in data.columns:
        raise Exception("The specified column is not in the specified dataframe")
    
    numeric_plot = alt.Chart(data, width=w, height=h
              ).mark_bar(
              ).encode(
                  x=alt.X(column, title=x_title, bin=alt.Bin(maxbins=30)),
                  y=alt.Y("count()", title="Number of Flights")
                  )
    return numeric_plot