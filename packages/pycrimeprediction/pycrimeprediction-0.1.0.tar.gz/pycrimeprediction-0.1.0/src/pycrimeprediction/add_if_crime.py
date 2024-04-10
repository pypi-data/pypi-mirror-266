import pandas as pd

def add_if_crime_feature(data):
    """
    Adds a binary column 'if_crime' to the DataFrame as the target value indicating whether the incident_subcategory is a criminal incident or not.

    If the incident_subcategory is one of the criminal_incident, then the column of 'if_crime' will be 1.
    If the incident_subcategory is not in one of the criminal_incident, then the column of 'if_crime' will be 0.

    Parameters:
    -----------
      data (DataFrame): A pandas DataFrame containing the incident data.
      The data should include the incident_subcategory as one of the features.
    
    Returns:
    --------
      DataFrame: A DataFrame with target 'if_crime' column.

    Examples:
    ---------
    >>> import pandas as pd
    >>> data = pd.DataFrame({"incident_subcategory": ["Vandalism", "Fraud"]})
    >>> add_if_crime_feature(data)
      incident_subcategory  if_crime
    0            Vandalism         1
    1                Fraud         1

    Notes:
    ------
    This function requires panda library for dataFrame.
    
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data should be a pandas DataFrame")
    
    criminal_incident = ["Larceny - From Vehicle", "Vandalism", "Larceny Theft - Other", "Motor Vehicle Theft",
                        "Simple Assault", "Drug Violation", "Aggravated Assault", "Fraud", "Theft From Vehicle",
                        "Burglary - Other", "Weapons Offense", "Intimidation", "Warrant", "Larceny - Auto Parts",
                        "Other Offenses", "Larceny Theft - From Building", "Larceny Theft - Shoplifting",
                        "Robbery - Other", "Burglary - Residential", "Robbery - Street",
                        "Traffic Violation Arrest", "Robbery - Commercial", "Larceny Theft - Pickpocket", "Forgery And Counterfeiting",
                        "Motor Vehicle Theft (Attempted)", "Burglary - Hot Prowl", "Prostitution",
                        "Burglary - Commercial", "Disorderly Conduct", "Arson",
                        "Larceny Theft - Bicycle", "Embezzlement",
                        "Extortion-Blackmail", "Sex Offense"]
    
    data['if_crime'] = data['incident_subcategory'].apply(lambda x: 1 if x in criminal_incident else 0)
    return data

