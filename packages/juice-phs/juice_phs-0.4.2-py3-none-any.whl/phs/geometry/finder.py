import spiceypy as spice
import logging
import numpy as np
from phs.utils.time import win2lst, sec2hhmmss
from phs.geometry.support import fov_expanded_boundaries


def target_in_fov(utc_start='', utc_end='',
                  interval=False, step=600,
                  fov='JUICE_JANUS',
                  observer=None, # Required when the FOV is not an ephemeris object.
                  target='SUN',
                  verbose=False,
                  abcorr='NONE'):
    """
    Check the visibility of a target in a Field of View (FOV) over a specified time interval.

    The condition of visibility is met as soon as the target is partially visible in the FOV.

    Parameters
    ----------
    utc_start : str, optional
        Start time in UTC format (default is '').
    utc_end : str, optional
        End time in UTC format (default is '').
    interval : SPICE window, optional
        Time interval specified as a SPICE window (default is False).
    step : int, optional
        Step size for time increments (default is 600).
    fov : str, optional
        Name of the Field of View (FOV) (default is 'JUICE_JANUS').
    observer : str, optional
        Name of the observer object (required when FOV is not an ephemeris object).
    target : str, optional
        Target object to check visibility (default is 'SUN').
    verbose : bool, optional
        Toggle verbose logging (default is False).
    abcorr : str, optional
        Aberration correction (default is 'NONE').
    **kwargs : dict, optional
        Additional keyword arguments.

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals when the target is visible in the FOV.
    rislis : list
        List of start and stop times within the detected intervals.

    Notes
    -----
    This function determines the visibility of a target in a specified Field of View (FOV) over a given time interval.
     It calculates the intervals during which the target is visible from the observer within the specified FOV.

    When 'interval' is False, 'utc_start' and 'utc_end' define the time interval to be analyzed.
    If 'interval' is provided, it overrides 'utc_start' and 'utc_end'.

    If 'observer' is not provided, it defaults to the FOV name.
    """
    if not interval:
        et_start = spice.utc2et(utc_start)
        et_stop = spice.utc2et(utc_end)
        cnfine = spice.cell_double(2)
        spice.wninsd(et_start, et_stop, cnfine)
    else:
        cnflst = win2lst(interval, verbose=False)
        utc_start = spice.et2utc(min(cnflst)[0], 'ISOC', 0, 70)
        utc_end = spice.et2utc(max(cnflst)[-1], 'ISOC', 0, 70)
        cnfine = interval

    maxlen = 40000
    riswin = spice.cell_double(maxlen)

    if not observer:
        observer = fov

    # First we calculate if the target is in the FOV
    spice.gftfov(fov, target, 'ELLIPSOID', f'IAU_{target}',
                 abcorr, observer, step, cnfine, riswin)

    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{target} not in {fov} FOV')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{target} in {fov} FOV')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis


def target_in_full_fov(utc_start='', utc_end='',
                       interval=False, step=10,
                       fov='JUICE_JANUS',
                       observer=None, # Required when the FOV is not an ephemeris object.
                       target='SUN',
                       verbose=False,
                       abcorr='NONE'):
    """
    Check the visibility of a target in a Field of View (FOV) over a specified time interval when
    the target completely fills the FOV.

    The condition of visibility is only met when the FOV is fully covered by the target.

    Parameters
    ----------
    utc_start : str, optional
        Start time in UTC format (default is '').
    utc_end : str, optional
        End time in UTC format (default is '').
    interval : SPICE window, optional
        Time interval specified as a SPICE window (default is False).
    step : int, optional
        Step size for time increments (default is 600).
    fov : str, optional
        Name of the Field of View (FOV) (default is 'JUICE_JANUS').
    observer : str, optional
        Name of the observer object (required when FOV is not an ephemeris object).
    target : str, optional
        Target object to check visibility (default is 'SUN').
    verbose : bool, optional
        Toggle verbose logging (default is False).
    abcorr : str, optional
        Aberration correction (default is 'NONE').
    **kwargs : dict, optional
        Additional keyword arguments.

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals when the target is visible in the FOV.
    rislis : list
        List of start and stop times within the detected intervals.

    Notes
    -----
    This function determines the visibility of a target in a specified Field of View (FOV) over a given time interval.
     It calculates the intervals during which the target is visible from the observer within the specified FOV.

    When 'interval' is False, 'utc_start' and 'utc_end' define the time interval to be analyzed.
    If 'interval' is provided, it overrides 'utc_start' and 'utc_end'.

    If 'observer' is not provided, it defaults to the FOV name.
    """
    if not observer:
        observer = fov
    target_frame = f'IAU_{target}'

    riswin_fov, rislis_fov = target_in_fov(utc_start=utc_start, utc_end=utc_end,
                                   interval=interval, step=step,
                                   fov=fov,
                                   observer=observer,  # Required when the FOV is not an ephemeris object.
                                   target=target,
                                   verbose=False,
                                   abcorr=abcorr)

    maxlen = 40000
    riswin = spice.cell_double(maxlen)

    # Now we calculate when the target is fully in the FOV
    fov_bounds, fov_frame = fov_expanded_boundaries(fov)


    # Now we need to find when all the vectors intersect with the target body.
    adjust = 0.0

    if not observer:
        observer = fov

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        for fov_bound in fov_bounds:
            try:
                srfpt, inet, obs2srf = spice.sincpt('ELLIPSOID', target, et, target_frame, abcorr, observer, fov_frame,
                                                    fov_bound)
            except:
                return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '>', 0, adjust, step, 20000, riswin_fov, riswin)

    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{target} not in {fov} FOV')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{target} in full {fov} FOV')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis


def full_target_in_fov(utc_start='', utc_end='',
                       interval=False, step=10,
                       fov='JUICE_JANUS',
                       observer=None, # Required when the FOV is not an ephemeris object.
                       target='SUN',
                       verbose=False,
                       abcorr='NONE'):
    """
    Check the visibility of a target in a Field of View (FOV) over a specified time interval when
    the target completely fills the FOV.

    The condition of visibility is only met when the FOV is fully covered by the target.

    Parameters
    ----------
    utc_start : str, optional
        Start time in UTC format (default is '').
    utc_end : str, optional
        End time in UTC format (default is '').
    interval : SPICE window, optional
        Time interval specified as a SPICE window (default is False).
    step : int, optional
        Step size for time increments (default is 600).
    fov : str, optional
        Name of the Field of View (FOV) (default is 'JUICE_JANUS').
    observer : str, optional
        Name of the observer object (required when FOV is not an ephemeris object).
    target : str, optional
        Target object to check visibility (default is 'SUN').
    verbose : bool, optional
        Toggle verbose logging (default is False).
    abcorr : str, optional
        Aberration correction (default is 'NONE').
    **kwargs : dict, optional
        Additional keyword arguments.

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals when the target is visible in the FOV.
    rislis : list
        List of start and stop times within the detected intervals.

    Notes
    -----
    This function determines the visibility of a target in a specified Field of View (FOV) over a given time interval.
     It calculates the intervals during which the target is visible from the observer within the specified FOV.

    When 'interval' is False, 'utc_start' and 'utc_end' define the time interval to be analyzed.
    If 'interval' is provided, it overrides 'utc_start' and 'utc_end'.

    If 'observer' is not provided, it defaults to the FOV name.
    """
    if not observer:
        observer = fov
    target_frame = f'IAU_{target}'

    riswin_fov, rislis_fov = target_in_fov(utc_start=utc_start, utc_end=utc_end,
                                   interval=interval, step=step,
                                   fov=fov,
                                   observer=observer,  # Required when the FOV is not an ephemeris object.
                                   target=target,
                                   verbose=False,
                                   abcorr=abcorr)

    maxlen = 40000
    riswin = spice.cell_double(maxlen)

    # Now we calculate when the target is fully in the FOV
    fov_bounds, fov_frame = fov_expanded_boundaries(fov)


    # Now we need to find when all the vectors intersect with the target body.
    adjust = 0.0

    if not observer:
        observer = fov

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        tar_not_in_fov_bound = 0
        for fov_bound in fov_bounds:
            try:
                srfpt, inet, obs2srf = spice.sincpt('ELLIPSOID', target, et, target_frame, abcorr, observer, fov_frame,
                                                    fov_bound)
            except:
                tar_not_in_fov_bound +=1

        if tar_not_in_fov_bound == len(tar_not_in_fov_bound):
            return et
        else:
            return -1* et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '>', 0, adjust, step, 20000, riswin_fov, riswin)

    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{target} not in {fov} FOV')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{target} in full {fov} FOV')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis


def los_target_intercept(utc_start='', utc_end='',
                         interval=False, step=200,
                         fov='JUICE_JANUS',
                         los_in_sc_frame=[0,0,1],
                         target='SUN',
                         verbose=False,
                         abcorr='NONE'):
    """
    Calculate when a given Line of Sight is intersectig with a target body.

    Parameters
    ----------
    utc_start : str, optional
        Start time in UTC format (default is '').
    utc_end : str, optional
        End time in UTC format (default is '').
    interval : SPICE window, optional
        Time interval specified as a SPICE window (default is False).
    step : int, optional
        Step size for time increments (default is 600).
    fov : str, optional
        Name of the Field of View (FOV) from which the Line of Sight is obtained (default is 'JUICE_JANUS').
    los_in_sc_frame : str, optional
        If no `fov` is provided, a vector with the Line of Sight direction WRT the JUICE_SPACECRAFT frame can be
        provided.
    target : str, optional
        Target object to check visibility (default is 'SUN').
    verbose : bool, optional
        Toggle verbose logging (default is False).
    abcorr : str, optional
        Aberration correction (default is 'NONE').
    **kwargs : dict, optional
        Additional keyword arguments.

    Returns
    -------
    riswin : spice.cell_double
        SPICE window containing time intervals when the target is visible in the FOV.
    rislis : list
        List of start and stop times within the detected intervals.

    Notes
    -----
    In order to define a `los_in_sc_frame` vector, the JUICE AGM Fixed Definitions can be a good starting point.
    """
    if not interval:
        et_start = spice.utc2et(utc_start)
        et_stop = spice.utc2et(utc_end)
        cnfine = spice.cell_double(2)
        spice.wninsd(et_start, et_stop, cnfine)
    else:
        cnflst = win2lst(interval, verbose=False)
        utc_start = spice.et2utc(min(cnflst)[0], 'ISOC', 0, 70)
        utc_end = spice.et2utc(max(cnflst)[-1], 'ISOC', 0, 70)
        cnfine = interval

    maxlen = 40000
    riswin = spice.cell_double(maxlen)

    target_frame = f'IAU_{target}'

    # Now we need to find when all the vectors intersect with the target body.
    adjust = 0.0

    if fov:
        _, los_frame, los, _, _ = spice.getfvn(fov, maxlen, maxlen, maxlen)
    else:
        los = los_in_sc_frame
        los_frame = 'JUICE_SPACECRAFT'
        fov = f'{los_in_sc_frame} WRT S/C'

    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        try:
            srfpt, inet, obs2srf = spice.sincpt('ELLIPSOID', target, et, target_frame, abcorr, 'JUICE', los_frame, los)
        except:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '>', 0, adjust, step, 20000, cnfine, riswin)

    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{target} not in {fov} FOV')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{fov} LOS {target} interception')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis


def los_terminator_crossing(utc_start='', utc_end='',
                            interval=False, step=10,
                            fov='JUICE_JANUS',
                            los_in_sc_frame=[0, 0, 1],
                            target='SUN',
                            verbose=False,
                            abcorr='NONE'):
    if not interval:
        et_start = spice.utc2et(utc_start)
        et_stop = spice.utc2et(utc_end)
        cnfine = spice.cell_double(2)
        spice.wninsd(et_start, et_stop, cnfine)
    else:
        cnflst = win2lst(interval, verbose=False)
        utc_start = spice.et2utc(min(cnflst)[0], 'ISOC', 0, 70)
        utc_end = spice.et2utc(max(cnflst)[-1], 'ISOC', 0, 70)
        cnfine = interval

    maxlen = 40000
    riswin = spice.cell_double(maxlen)

    target_frame = f'IAU_{target}'

    # Now we need to find when all the vectors intersect with the target body.
    adjust = 0.0

    if fov:
        _, los_frame, los, _, _ = spice.getfvn(fov, maxlen, maxlen, maxlen)
    else:
        los = los_in_sc_frame
        los_frame = 'JUICE_SPACECRAFT'
        fov = f'{los_in_sc_frame} WRT S/C'


    @spice.utils.callbacks.SpiceUDFUNS
    def gfq(et):
        try:
            srfpt, _, _ = spice.sincpt('ELLIPSOID', target, et, target_frame, abcorr, 'JUICE', los_frame, los)
            _, _, _, incdnc, _ = spice.ilumin('ELLIPSOID', target, et, target_frame, abcorr, 'JUICE', srfpt)
            incdnc *= spice.dpr()
        except:
            incdnc = 180
        if incdnc > 90:
            return -1 * et
        return et

    @spice.utils.callbacks.SpiceUDFUNB
    def gfdecrx(udfuns, et):
        return spice.uddc(udfuns, et, 10)

    spice.gfuds(gfq, gfdecrx, '=', 0, adjust, step, 20000, cnfine, riswin)


    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{fov} not crossing the {target} terminator')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{fov} crossing the {target} terminator')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis


def star_in_fov(utc_start='', utc_end='',
                interval=False, step=600,
                ins_fov='JUICE_MAJIS_ENVELOPE',
                observer='JUICE',
                star=None,
                ra=None,
                dec=None,
                verbose=True,
                abcorr='S'):

    if not interval:
        et_start = spice.utc2et(utc_start)
        et_stop = spice.utc2et(utc_end)
        cnfine = spice.cell_double(2)
        spice.wninsd(et_start, et_stop, cnfine)
    else:
        cnflst = win2lst(interval, verbose=False)
        utc_start = spice.et2utc(min(cnflst)[0], 'ISOC', 0, 70)
        utc_end = spice.et2utc(max(cnflst)[-1], 'ISOC', 0, 70)
        cnfine = interval
        et_start = min(cnflst)[0]

    if star:
        ra, dec = star2kpool(star, verbose=verbose)
        ra = spice.convrt(ra, 'DEGREES', 'RADIANS')
        dec = spice.convrt(dec, 'DEGREES', 'RADIANS')
    else:
        if ra and dec:
            pass
        else:
            logging.error('Star nor RA/DEC inputs provided')
            raise

    #          /.
    #          Create a unit direction vector pointing from observer to star.
    #          We'll assume the direction is constant during the confinement
    #          window, and we'll use et0 as the epoch at which to compute the
    #          direction from the spacecraft to the star.
    #
    #          The data below are for the star with catalog number 6000
    #          in the Hipparcos catalog. Angular units are degrees; epochs
    #          have units of Julian years and have a reference epoch of J1950.
    #          The reference frame is J2000.
    #          ./
    #          catno        = 6000;
    #
    #          parallax_deg = 0.000001056;
    #
    #          ra_deg_0     = 19.290789927;
    #          ra_pm        = -0.000000720;
    #          ra_epoch     = 41.2000;
    #
    #          dec_deg_0    =  2.015271007;
    #          dec_pm       =  0.000001814;
    #          dec_epoch    = 41.1300;
    #
    #          rframe       = "J2000";
    #
    #          /.
    #          Correct the star's direction for proper motion.
    #
    #          The argument t represents et0 as Julian years past J1950.
    #          ./
    #          t         = et0/jyear_c()  +  ( j2000_c()- j1950_c() )/365.25;
    #
    #          dtra      = t - ra_epoch;
    #          dtdec     = t - dec_epoch;
    #
    #          ra_deg    = ra_deg_0  +  dtra  * ra_pm;
    #          dec_deg   = dec_deg_0 +  dtdec * dec_pm;
    #
    #          ra        = ra_deg  * rpd_c();
    #          dec       = dec_deg * rpd_c();
    #          radrec_c ( 1.0, ra, dec, starpos );
    #
    #          /.
    #          Correct star position for parallax applicable at
    #          the Cassini orbiter's position. (The parallax effect
    #          is negligible in this case; we're simply demonstrating
    #          the computation.)
    #          ./
    #          parallax = parallax_deg * rpd_c();
    #          stardist = AU / tan(parallax);
    #
    #          /.
    #          Scale the star's direction vector by its distance from
    #          the solar system barycenter. Subtract off the position
    #          of the spacecraft relative to the solar system barycenter;
    #          the result is the ray's direction vector.
    #          ./
    #          vscl_c   ( stardist, starpos, starpos );
    #
    #          spkpos_c ( "cassini", et0, "J2000",  "NONE",
    #                     "solar system barycenter", pos,  &lt );
    #
    #          vsub_c   ( starpos, pos, raydir );
    ray2star = spice.radrec(1.0, ra, dec)
    rframe = 'J2000'

    nintvls = 40000
    adjust = 0.0
    riswin = spice.cell_double(nintvls)

    spice.gfrfov(ins_fov, ray2star, rframe,  abcorr, observer, step, cnfine, riswin)

    # The function wncard returns the number of intervals
    # in a SPICE window.
    winsiz = spice.wncard(riswin)

    # Define the list of events.
    rislis = []

    if winsiz == 0 and verbose:
        logging.warning(f'{star} not in {ins_fov} FOV.')
    else:
        # Display the visibility time periods.
        if verbose:
            logging.info('')
            logging.info(f'{star} in {ins_fov} FOV')
            logging.info('------------------------------------------------------')
            logging.info(f'Interval start:     {utc_start}')
            logging.info(f'Interval end:       {utc_end}')
            logging.info(f'Step [s]:           {step}')
            logging.info('-----------------------------------------------------')

        for i in range(winsiz):
            # Fetch the start and stop times of
            # the ith interval from the search result
            # window riswin.
            [intbeg, intend] = spice.wnfetd(riswin, i)

            # Convert the time to a UTC calendar string.
            timstr_beg = spice.et2utc(intbeg, 'ISOC', 0, 70)
            timstr_end = spice.et2utc(intend, 'ISOC', 0, 70)
            duration = intend - intbeg

            # Write the string to standard output.
            if verbose:
                logging.info(f'{timstr_beg} - {timstr_end}: {sec2hhmmss(duration)}')

            rislis.append([intbeg, intend])
        if verbose:
            logging.info('-----------------------------------------------------')
            logging.info(f'Number of results: {len(rislis)}')
            logging.info('')

    return riswin, rislis