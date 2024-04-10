import spiceypy as spice
from phs.geometry.derived import subsc_zsc_offset, sun_px_angle, sun_pz_angle
from phs.modelling.swi import swi_violation

def majis_constraint_radiator_illumination(utc_start, utc_stop, step=30, verbose=True):
    """
    MAJIS Radiator Illumination constraint check.

    Geometry Finder function for detecting intervals when the +X Panel is illuminated.

    Parameters
    ----------
    utc_start : str
        Start time in UTC format.
    utc_stop : str
        Stop time in UTC format.
    step : int, optional
        Step size for time increments (default is 60).

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals of illumination.
    rislis : list
        List of start and stop times within the detected intervals.
    """
    et_start = spice.utc2et(utc_start)
    et_stop = spice.utc2et(utc_stop)
    riswin = spice.cell_double(40000)
    cnfine = spice.cell_double(2)
    spice.wninsd(et_start, et_stop, cnfine)
    adjust = 0.0

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        angle = sun_px_angle(utc='', et=et)
        if angle > 90:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '>', 0, adjust, step, 20000, cnfine, riswin)

    # The function wncard returns the number of intervals in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0:
        pass
    else:
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
                print(f'MAJIS illumination violation: {timstr_beg} - {timstr_end}')

            rislis.append([intbeg, intend])

    return riswin, rislis


def rime_constraint_offpointing(utc_start, utc_stop, target='GANYMEDE', step=60):
    """
    RIME Off-pointing constraint check.

    Geometry Finder function for identifying off-pointing intervals of RIME instrument
    towards a specific target within the given time frame.

    Parameters
    ----------
    utc_start : str
        Start time in UTC format.
    utc_stop : str
        Stop time in UTC format.
    target : str, optional
        Target celestial body (default is 'GANYMEDE').
    step : int, optional
        Step size for time increments (default is 60).

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals of off-pointing.
    rislis : list
        List of start and stop times within the detected intervals.
    """
    et_start = spice.utc2et(utc_start)
    et_stop = spice.utc2et(utc_stop)
    riswin = spice.cell_double(40000)
    cnfine = spice.cell_double(2)
    spice.wninsd(et_start, et_stop, cnfine)
    adjust = 0.0

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        sun_mz_angle = subsc_zsc_offset(utc='', et=et, target=target)
        if sun_mz_angle > 5:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '<', 0, adjust, step, 20000, cnfine, riswin)

    # The function wncard returns the number of intervals in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0:
        pass
    else:
        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)

            # Write the string to standard output.
            print(f'RIME off-pointing violation: {timstr_beg} - {timstr_end}')

            rislis.append([intbeg, intend])

    return riswin, rislis


def swi_constraint_pointing(utc_start, utc_stop, step=60, target='JUPITER'):
    """
    SWI Pointing Stability constraint check.

    Geometry Finder function for determining intervals when the spacecraft
    pointing violates constraints towards a specific target.

    Parameters
    ----------
    utc_start : str
        Start time in UTC format.
    utc_stop : str
        Stop time in UTC format.
    step : int, optional
        Step size for time increments (default is 60).
    target : str, optional
        Target celestial body (default is 'JUPITER').

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals of violation.
    rislis : list
        List of start and stop times within the detected intervals.
    """
    et_start = spice.utc2et(utc_start)
    et_stop = spice.utc2et(utc_stop)
    riswin = spice.cell_double(40000)
    cnfine = spice.cell_double(2)
    spice.wninsd(et_start, et_stop, cnfine)
    adjust = 0.0

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        violation = swi_violation(utc='', et=et, target=target)
        if violation:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '<', 0, adjust, step, 20000, cnfine, riswin)

    # The function wncard returns the number of intervals in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0:
        pass
    else:
        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)

            # Write the string to standard output.
            print(f'SWI pointing violation: {timstr_beg} - {timstr_end}')

            rislis.append([intbeg, intend])

    return riswin, rislis


def sc_pz_panel_illumination(utc_start, utc_stop, step=30, verbose=True):
    """
    S/C +Z Panel Illumination constraint check.

    Geometry Finder function for detecting intervals when the +Z Panel is illuminated.

    Parameters
    ----------
    utc_start : str
        Start time in UTC format.
    utc_stop : str
        Stop time in UTC format.
    step : int, optional
        Step size for time increments (default is 60).

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals of illumination.
    rislis : list
        List of start and stop times within the detected intervals.
    """
    et_start = spice.utc2et(utc_start)
    et_stop = spice.utc2et(utc_stop)
    riswin = spice.cell_double(40000)
    cnfine = spice.cell_double(2)
    spice.wninsd(et_start, et_stop, cnfine)
    adjust = 0.0

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        angle = sun_pz_angle(utc='', et=et)
        if angle > 89.98:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '>', 0, adjust, step, 20000, cnfine, riswin)

    # The function wncard returns the number of intervals in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0:
        pass
    else:
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
                print(f'+Z Panel illumination: {timstr_beg} - {timstr_end}')

            rislis.append([intbeg, intend])

    return riswin, rislis