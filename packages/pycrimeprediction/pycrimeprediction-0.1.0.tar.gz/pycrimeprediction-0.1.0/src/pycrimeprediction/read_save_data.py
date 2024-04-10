import pandas as pd

def read_save_data(input_path: str, output_path: str):
    """
    Read data and save as csv file to output_path

    Parameters:
    -----------
    input_path: str
        The path of the csv file to be read

    output_path: str
        The path for new csv file to be written to

    Returns:
    --------
    DataFrame
        Representation of the csv data as a dataFrame
        
    Examples:
    ---------
    >>> data = read_save_data('dataUrl', 'newFilePath') # replace ('dataUrl', 'newFilePath') with the actual url of data and filepath to be written to
    >>> print(data)

    Notes:
    ------
    This function uses the pandas library to read the data

    """

    if not isinstance(input_path, str) or not isinstance(output_path, str):
        raise TypeError('both input_path and output_path should be strings')

    # Read data from the input path
    raw_data = pd.read_csv(input_path, parse_dates=['incident_datetime'], date_format='%Y-%m-%d %H:%M:%S')
    
    # Save the data to the output path
    raw_data.to_csv(output_path, index=False)

    return raw_data