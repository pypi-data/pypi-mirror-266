
def get_time_period(hour:int, minute:int):
    """
    get the correct time period for the incident time

    generate the time period ('Late Night', 'Morning', 'Afternoon', 'Evening', 'Night') 
    indicating the proper time period of the incident

    Parameters:
    -----------
    hour: int
        The input hour of the incident from the hour column of the dataframe

    minute: int
        The input minute of the incident from the minute column of the dataframe 

    Returns:
    --------
    String
        A string indicate the correct time period using the given hour and minute.
        ('Late Night', 'Morning', 'Afternoon', 'Evening', 'Night')
        
    Examples:
    ---------
    >>> time_period = get_time_period(3, 12) # replace (3, 12) with the actural hour and miniute
    >>> print(time_period)

    Notes:
    ------
    This function does not need extra library. It will provide the indication of the time period from the given data.

    """
    if not isinstance(hour, int) or not isinstance(minute, int):
         raise TypeError('Both hour and minute input should be integer')
    if 0 < hour < 6 or (hour == 6 and minute == 0):
        return 'Late Night'
    elif 6 < hour < 12 or (hour == 6 and minute > 0) or (hour == 12 and minute == 0):
        return 'Morning'
    elif 12 < hour < 18 or (hour == 12 and minute > 0) or (hour == 18 and minute == 0):
        return 'Afternoon'
    elif 18 < hour < 21 or (hour == 18 and minute > 0) or (hour == 21 and minute == 0):
        return 'Evening'
    else:
        return 'Night'

