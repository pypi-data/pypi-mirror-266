def hms_string(sec_elapsed) -> str:
    """
    Hours Minutes Seconds String

    This function that takes in number of seconds and return a well formatted string label which looks as '0:00:00.00'

    Parameters
    ----------
    sec_elapsed : int
        Takes in the number of seconds elapsed

    Returns
    -------
    time : str
        A string formatted version of time in form '0:00:00.00'

    See Also
    --------
    normalize_image : This function takes in an image that need to be normalized, so that it can be plotted using matplotlib.


    Examples
    --------
    >>> start = time.time()
    >>> for i in range(1000):pass
    >>> end = time.time()
    '0:00:00.01'
    """

    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


__all__ = [hms_string]
