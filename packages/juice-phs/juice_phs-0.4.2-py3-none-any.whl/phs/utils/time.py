import spiceypy as spice
from datetime import datetime

def utc2win(utc_start, utc_stop):
    '''UTC to SPICE Window conversion.

    Parameters
    ----------
    utc_start : str
       Start time in UTC format ``YYYY-MM-DDThh:mm:ss``.
    utc_stop : str
       Stop time in UTC format ``YYYY-MM-DDThh:mm:ss``.

    Returns
    -------
    cnfine : spice.cell_double(2)
       SPICE Window with indicated start time and stop times.

    '''
    et_start = spice.utc2et(utc_start)
    et_stop = spice.utc2et(utc_stop)
    cnfine = spice.cell_double(2)
    spice.wninsd(et_start, et_stop, cnfine)

    return cnfine


def list2uctlist(ephemeris_dict):
    """
    Convert a dictionary of ephemeris intervals from ET to UTC.

    Parameters
    ----------
    ephemeris_dict : dict
        Dictionary with keys as celestial body names and values as lists of ET intervals.

    Returns
    -------
    dict
        Dictionary containing UTC intervals for each celestial body from the input dictionary.
    """
    utc_dict = {}
    for body, intervals in ephemeris_dict.items():
        utc_intervals = []
        for interval in intervals:
            start_et, end_et = interval
            start_utc = spice.et2utc(start_et, 'C', 3)
            end_utc = spice.et2utc(end_et, 'C', 3)
            utc_intervals.append([start_utc, end_utc])
        utc_dict[body] = utc_intervals

    return utc_dict

def win2lst(riswin, verbose=False):
    """
    Convert a SPICE window to a list of time intervals.

    Parameters
    ----------
    riswin : SpiceWindow
        The SPICE window containing time intervals to be converted.

    verbose : bool, optional
        If True, print the window time intervals to standard output.
        Default: False

    Returns
    -------
    List[List[float]]
        A list of time intervals represented as pairs of start and end times.
        Each time interval is represented by a list containing the start and end times as floats.
    """
    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if verbose:
        print(f'Window time intervals:')
    for i in range(winsiz):
        # Fetch the start and stop times of
        # the ith interval from the search result
        # window riswin.
        [intbeg, intend] = spice.wnfetd(riswin, i)

        # Convert the time to a UTC calendar string.
        timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
        timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)

        # Write the string to standard output.
        if verbose:
            print(f'{timstr_beg} - {timstr_end}')

        rislis.append([intbeg, intend])

    return rislis


def win2utc(riswin, verbose=False):
    """
    Convert SPICE window intervals to a list of UTC time intervals.

    Parameters
    ----------
    riswin : SPICE window
        SPICE window containing time intervals.
    verbose : bool, optional
        Verbosity flag, if True, prints the window time intervals (default: False).

    Returns
    -------
    list
        List of lists containing UTC time intervals in the format [[start_time_UTC, end_time_UTC], ...].
    """
    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if verbose:
        print(f'Window time intervals:')
    for i in range(winsiz):
        # Fetch the start and stop times of
        # the ith interval from the search result
        # window riswin.
        [intbeg, intend] = spice.wnfetd(riswin, i)

        # Convert the time to a UTC calendar string.
        timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
        timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)

        # Write the string to standard output.
        if verbose:
            print(f'{timstr_beg} - {timstr_end}')

        rislis.append([timstr_beg, timstr_end])

    return rislis


def sec2hhmmss(seconds):
    '''Seconds to ``hh:mm:ss`` conversion.

    Parameters
    ----------
    seconds : float
       Seconds to be converted

    Returns
    -------
    hhmmss : str
       secods in ``hh:mm:ss`` format

    '''
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    hhmmss = "%d:%02d:%02d" % (hour, minutes, seconds)
    return hhmmss


def et_to_datetime(et, scale='TDB'):
    """
    convert a SPICE ephemerides epoch (TBD seconds) to a python datetime
    object. The default time scale returned will be TDB but can be set
    to any of the accepted SPICE time scales.

    Args:
        et (float): SPICE ephemerides sceonds (TBD)
        scale (str, optional): time scale of output time (default: TDB)

    Returns:
        datetime: python datetime
    """
    t = spice.timout(et, 'YYYY-MON-DD HR:MN:SC.### ::{}'.format(scale), 41)
    return datetime.strptime(t, '%Y-%b-%d %H:%M:%S.%f')


def parse_utc_datetime(utc_str):
    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass

    raise ValueError("Invalid UTC datetime format")