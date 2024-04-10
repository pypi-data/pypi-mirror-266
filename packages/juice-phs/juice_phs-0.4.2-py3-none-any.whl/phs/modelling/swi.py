import numpy as np
import spiceypy as spice


def check_swi_violation(angular_diameter, x, y, dx, dy):
    """
    SWI Constraint Violation Definition.

    Parameters
    ----------
    angular_diameter : float
        Angular diameter of the target of SWI in degrees.
    x : float
        Offset from target center in SC coordinates in degrees.
    y : float
        Offset from target center in SC coordinates in degrees.
    dx : float
        Drift rate in x in degrees per second.
    dy : float
        Drift rate in y in degrees per second.

    Returns
    -------
    flags : dict
        Dictionary with messages indicating specific violations.
    violation : bool
        True if any violation is found, False otherwise.

    Notes
    -------

    Author: rezac@mps.mpg.de
    Verison 0, Nov. 27, 2023.

    The purpose of this function is to check whether provided pointing violates
    SWI FOV and drift constraints for its "PRIME" defined blocks.
    ------------------------------------------------------------------------
    AT = along track mechanism (@ Jupiter phase)
    CT = cross track mechanism (@ Jupiter phase)

    Both mechanisms are currently assumed to be perfectly alligned with X and
    Y axes of the SC.

    Half-range AT and CT are:
    From SWI_IK: AT = 72.057295, CT = 4.357295 [deg]. However, we use for now
    values from JUI-MPS-SWI-TR-069_i2.0: AT=71.8965 and CT=4.318 [deg]. The
    final decision on these values will be made based on data from NECP and PCWs.
    ------------------------------------------------------------------------

    As of Version 0, the SWI boresight direction has been determined from NECP
    data to be offset by 39 and 58 steps in AT and CT respectively, which
    translates into
    AT0 = 39*29.92/3600 = 0.324 [deg]
    CT0 = 58*8.67/3600  = 0.140 [deg]

    This correction assume JUICE +Z axis to be pointing exactly at 0,0 in SC
    frame. We lump every mis-allignement on SC
    as well as SWI own mechanism offset into this single number for AT and CT.
    ------------------------------------------------------------------------

    As of Version 0 the drift rate of AT and CT constraint is estimated from
    wind requirement of as 1/10 of 600 GHz beam per 30 min, 6e-6 deg/sec. This
    was routinely met during NECP.
    ------------------------------------------------------------------------

    -Routine not vectorized...
    -Right now relative offset wrt target center. Later fraction of disk can be
     developed...

    """
    ATMAX = 71.8965
    CTMAX = 4.318
    AT0 = 0.324
    CT0 = 0.140
    DRMAX = 6.0e-6

    flags = {'AT': 'OK', 'CT': 'OK', 'ATDRIFT': 'OK', 'CTDRIFT': 'OK'}
    violation = False

    if (np.abs(x) >= (ATMAX + AT0)):
        flags['AT'] = 'Pointing out of AT range of SWI'
        violation = True
    elif (np.abs(y) >= (CTMAX + CT0)):
        flags['CT'] = 'Pointing out of CT range of SWI'
        violation = True
    elif (np.abs(dx) > DRMAX):
        flags['ATDRIFT'] = 'Drift along AT out of range of SWI'
        violation = True
    elif (np.abs(dy) > DRMAX):
        flags['CTDRIFT'] = 'Drift along CT out of range of SWI'
        violation = True
    else:
        pass

    return flags, violation


def swi_metrics(et, target='JUPITER', abcorr='LT+S'):
    """
    Compute angular measurements and rates for a spacecraft relative to a target.

    Parameters
    ----------
    et : float
        Ephemeris time (seconds past J2000 TDB).
    target : str, optional
        Target body (default is 'JUPITER').
    abcorr : str, optional
        Aberration correction (default is 'LT+S').

    Returns
    -------
    float
        X-component angular measurement (degrees).
    float
        Y-component angular measurement (degrees).
    float
        X-component angular rate (degrees per second).
    float
        Y-component angular rate (degrees per second).
    """
    sc2tar, lt = spice.spkezr(target, et, 'JUICE_SPACECRAFT', abcorr, 'JUICE')
    x = np.arcsin(sc2tar[0]/np.linalg.norm(sc2tar))*spice.dpr()
    y = np.arcsin(sc2tar[1]/np.linalg.norm(sc2tar))*spice.dpr()

    dx = np.arcsin(sc2tar[3]/np.linalg.norm(sc2tar))*spice.dpr()
    dy = np.arcsin(sc2tar[4]/np.linalg.norm(sc2tar))*spice.dpr()

    return x, y, dx, dy


def swi_violation(utc: str = '', et = None, target='JUPITER', abcorr='LT+S', verbose=False):
    """
    Check for SWI constraint violation based on spacecraft-target angular metrics.

    Parameters
    ----------
    utc : str, optional
        UTC time format (default is '').
    et : float, optional
        Ephemeris time (seconds past J2000 TDB).
    target : str, optional
        Target body (default is 'JUPITER').
    abcorr : str, optional
        Aberration correction (default is 'LT+S').
    verbose : bool, optional
        Toggle to display verbose output (default is False).

    Returns
    -------
    bool
        True if violation is detected, otherwise False.
    """
    if utc:
        et = spice.utc2et(str(utc))
    else:
        utc = spice.et2utc(et, 'ISOC', 0, 42)

    x, y, dx, dy = swi_metrics(et, target, abcorr)
    angular_diameter = 1
    flags, violation = check_swi_violation(angular_diameter, x, y, dx, dy)

    if verbose:
        message = ''
        for key, value in flags.items():
            if value != 'OK':
                message += f'Violation: {value}'
        print(f"{utc} SWI {message}" )
        print(f"                    [x={x:.2f}deg, y={y:.2f}deg, dx={dx*1e6:.2f}Mdeg/s, y={dy*1e6:.2f}Mdeg/s]")

    if violation:
        return True
    else:
        return False


def swi_metrics(et, target='JUPITER', abcorr='LT+S'):
    """
    Compute angular measurements and rates for a spacecraft relative to a target.

    Parameters
    ----------
    et : float
        Ephemeris time (seconds past J2000 TDB).
    target : str, optional
        Target body (default is 'JUPITER').
    abcorr : str, optional
        Aberration correction (default is 'LT+S').

    Returns
    -------
    float
        X-component angular measurement (degrees).
    float
        Y-component angular measurement (degrees).
    float
        X-component angular rate (degrees per second).
    float
        Y-component angular rate (degrees per second).
    """
    sc2tar, lt = spice.spkezr(target, et, 'JUICE_SPACECRAFT', abcorr, 'JUICE')
    x = np.arcsin(sc2tar[0]/np.linalg.norm(sc2tar))*spice.dpr()
    y = np.arcsin(sc2tar[1]/np.linalg.norm(sc2tar))*spice.dpr()

    dx = np.arcsin(sc2tar[3]/np.linalg.norm(sc2tar))*spice.dpr()
    dy = np.arcsin(sc2tar[4]/np.linalg.norm(sc2tar))*spice.dpr()

    return x, y, dx, dy