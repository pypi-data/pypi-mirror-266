"""
Created on January 2023
@author: Marc Costa Sitja (ESA/ESAC)
"""
import spiceypy as spice
from planetary_coverage import MetaKernel, ESA_MK
from pathlib import Path
from shutil import copy
import math
import plotly.graph_objects as go
import datetime

from phs.utils.time import et_to_datetime

from spiceypy.utils.support_types import *


def cov_ck_ker(ck, object, support_ker=list(), time_format='UTC',
               report=False, unload=True):
    """
    Provides time coverage summary for a given object for a given CK file.
    Several options are available. This function is based on the following
    SPICE API:
    http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/spice/ckcov_c.html
    The NAIF utility CKBRIEF can be used for the same purpose.
    :param ck: CK file to be used
    :type mk: str
    :param support_ker: Support kernels required to run the function. At least
       it should be a leapseconds kernel (LSK) and a Spacecraft clock kernel
       (SCLK) optionally a meta-kernel (MK) which is highly recommended. It
       is optional since the kernels could have been already loaded.
    :type support_ker: Union[str, list]
    :param object: Ephemeris Object to obtain the coverage from.
    :type object: str
    :param time_format: Output time format; it can be 'UTC', 'CAL' (for TDB
       in calendar format), 'TDB' or 'SPICE'. Default is 'TDB'.
    :type time_format: str
    :param global_boundary: Boolean to indicate whether if we want all the
       coverage windows or only the absolute start and finish coverage times.
    :type global_boundary: bool
    :param report: If True prints the resulting coverage on the screen.
    :type report: bool
    :param unload: If True it will unload the input meta-kernel.
    :type unload: bool
    :return: Returns a list with the coverage intervals.
    :rtype: list
    """
    spice.furnsh(ck)

    if support_ker:

        if isinstance(support_ker, str):
            support_ker = [support_ker]

        for ker in support_ker:
            spice.furnsh(ker)

    object_id = spice.namfrm(object)
    MAXIV = 200000
    WINSIZ = 2 * MAXIV
    MAXOBJ = 100000

    ck_ids = spice.support_types.SPICEINT_CELL(MAXOBJ)
    try:
        ck_ids = spice.ckobj(ck, outCell=ck_ids)
    except:
        ck_ids = spice.ckobj(ck)

    if object_id in ck_ids:

        object_cov = spice.support_types.SPICEDOUBLE_CELL(WINSIZ)
        spice.scard, 0, object_cov
        object_cov = spice.ckcov(ck=ck, idcode=object_id,
                                      needav=False, level='INTERVAL',
                                      tol=0.0, timsys='TDB',
                                      cover=object_cov)

    else:
        if unload:
            spice.unload(ck)
            if support_ker:

                if isinstance(support_ker, str):
                    support_ker = [support_ker]

                for ker in support_ker:
                    spice.unload(ker)

        return False

    if time_format == 'SPICE':
        boundaries = object_cov

    else:
        boundaries = cov_int(object_cov=object_cov,
                             object_id=object_id,
                             kernel=ck,
                             time_format=time_format, report=report)

    if unload:
        spice.unload(ck)
        if support_ker:

            if isinstance(support_ker, str):
                support_ker = [support_ker]

            for ker in support_ker:
                spice.unload(ker)

    return boundaries


def cov_int(object_cov, object_id, kernel, time_format='UTC',
            global_boundary=False, report=False):
    """
    Generates a list of time windows out of a SPICE cell for which either
    the SPICE API spkcov_c or ckcov_c have been run.
    :param object_cov: SPICE
    :type object_cov:
    :param object_id: Object ID or Name for which we provide the coverage
    :type object_id: Union[str, int]
    :param kernel: Kernel name for which the coverage is being checked
    :type kernel: str
    :param time_format: Desired output format; 'UTC' or 'CAL'
    :type time_format: str
    :param global_boundary: Boolean to indicate whether if we want all the coverage windows or only the absolute start and finish coverage times
    :type global_boundary: bool
    :param report: If True prints the resulting coverage on the screen
    :type report: bool
    :return: Time Windows in the shape of a list
    :rtype: list
    """
    boundaries = False

    if '/' in kernel:
        kernel = kernel.split('/')[-1]

    #
    # Reporting should only be activated if we are not asking for global
    # boundaries.
    #
    if report and not global_boundary:

        try:
            body_name = spice.bodc2n(object_id)
        except:
            body_name = spice.frmnam(object_id, 60)

        print("Coverage for {} in {} [{}]:".format(body_name, kernel,
                                                   time_format))

    number_of_intervals = list(range(spice.wncard(object_cov)))
    interval_start_list = []
    interval_finish_list = []
    coverage = []

    for element in number_of_intervals:
        et_boundaries = spice.wnfetd(object_cov, element)

        if time_format == 'CAL' or time_format == 'UTC':
            boundaries = et2cal(et_boundaries, format=time_format)
        else:
            boundaries = et_boundaries

        interval_start = boundaries[0]
        interval_finish = boundaries[1]


        if report and not global_boundary:

            print("Interval: {} - {}\n".format(boundaries[0],
                                               boundaries[1]))

        coverage.append(interval_start)
        coverage.append(interval_finish)
        interval_start_list.append(interval_start)
        interval_finish_list.append(interval_finish)


    #
    # If the global_boundary parameter is set the only output is the global
    # coverage start and finish
    #
    if global_boundary:

        start_time = min(interval_start)
        finish_time = max(interval_finish)

        coverage = et2cal([start_time, finish_time], format=time_format)

    return coverage


def et2cal(time, format='UTC', support_ker=False, unload=False):
    """
    Converts Ephemeris Time (ET) into UTC or Calendar TDB (CAL) time. Accepts
    a single time or a lists of times. This function assumes that the support
    kernels (meta-kernel or leapseconds kernel) has been loaded.
    :param time: Input ET time
    :type time: Union[float, list]
    :param format: Desired output format; 'UTC' or 'CAL'
    :type format: str
    :param unload: If True it will unload the input meta-kernel
    :type unload: bool
    :return: Output time in 'UTC', 'CAL' or 'TDB'
    :rtype: Union[str, list]
    """
    timlen = 62
    out_list = []

    if support_ker:
        spice.furnsh(support_ker)

    if isinstance(time, float) or isinstance(time, str):
        time = [time]

    for element in time:

        if format == 'UTC':
            out_elm = spice.et2utc(element, 'ISOC', 3)

        elif format == 'CAL':
            out_elm = spice.timout(element, "YYYY-MM-DDTHR:MN:SC.###::TDB", timlen)
        else:
            out_elm = element

        out_list.append(out_elm)

    if len(out_list) == 1:
        out_time = out_list[0]
    else:
        out_time = out_list

    if unload:
        spice.unload(support_ker)

    return out_time


def cov_spk_ker(spk, object=False, time_format='UTC', support_ker ='',
                report=False, unload=True):
    """
    Provides time coverage summary for a given object for a given SPK file.
    Several options are available. This function is based on the following
    SPICE API:
    http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/spice/spkcov_c.html
    The NAIF utility BRIEF can be used for the same purpose.
    :param spk: SPK file to be used
    :type mk: str
    :param support_ker: Support kernels required to run the function. At least it should be a leapseconds kernel (LSK) and optionally a meta-kernel (MK)
    :type support_ker: Union[str, list]
    :param object: Ephemeris Object or list of objects to obtain the coverage from
    :type object: str
    :param time_format: Output time format; it can be 'UTC', 'CAL' or 'SPICE' (for TDB in calendar format) or 'TDB'. Default is 'TDB'
    :type time_format: str
    :param global_boundary: Boolean to indicate whether if we want all the coverage windows or only the absolute start and finish coverage times
    :type global_boundary: bool
    :param report: If True prints the resulting coverage on the screen
    :type report: bool
    :param unload: If True it will unload the input meta-kernel
    :type unload: bool
    :return: Returns a list with the coverage intervals
    :rtype: list
    """
    spice.furnsh(spk)
    object_id = []
    boundaries = []

    if object and not isinstance(object, list):
        object = [object]

    if support_ker:

        if isinstance(support_ker, str):
            support_ker = [support_ker]

        for ker in support_ker:
            spice.furnsh(ker)

    maxwin = 2000

    spk_ids = spice.spkobj(spk)

    if not object:
        object_id = spk_ids
        object = []
        for id in spk_ids:
            object.append(spice.bodc2n(id))
    else:
        for element in object:
            object_id.append(spice.bodn2c(element))

    for id in object_id:

        if id in spk_ids:

            object_cov = SPICEDOUBLE_CELL(maxwin)
            spice.spkcov(spk, id, object_cov)

            cov = cov_int(object_cov=object_cov,
                                      object_id=id,
                                      kernel=spk,
                                      time_format=time_format,
                                      report=report)

        else:
            if report:
                print('{} with ID {} is not present in {}.'.format(object,
                                                             id, spk))
            if unload:
                spice.unload(spk)
                if support_ker:

                    if isinstance(support_ker, str):
                        support_ker = [support_ker]

                    for ker in support_ker:
                        spice.unload(ker)
            return False

        if time_format == 'SPICE':
            boundaries.append(object_cov)
        else:
            boundaries.append(cov)

    if unload:
        spice.unload(spk)
        if support_ker:

            if isinstance(support_ker, str):
                support_ker = [support_ker]

            for ker in support_ker:
                spice.unload(ker)

    return boundaries

def ck_coverage_timeline(mk, frame_list=['JUICE_SPACECRAFT_PLAN', 'JUICE_SPACECRAFT_MEAS'], height=0):

    cov_start = []
    cov_finsh = []
    kernels = []

    with open(mk, 'r') as f:
        for line in f:
            if '/ck/' in line and 'prelaunch' not in line:
                kernels.append(line.split('/ck/')[-1].strip().split("'")[0])
            if 'PATH_VALUES' in line and '=' in line:
                path = line.split("'")[1] + '/ck/'

    kernels = list(reversed(kernels))
    ck_kernels = []
    colors = []

    for kernel in kernels:
        for frame in frame_list:
            cov = cov_ck_ker(path + kernel, frame, support_ker=mk, time_format='TDB')

            if cov:
                color = "chartreuse"

                if 'meas' in kernel: color = 'cyan'
                elif 'att' in kernel: color = 'orange'
                elif 'crema' in kernel: color = 'lawngreen'
                elif 'ptr_soc' in kernel: color = 'coral'

                cov_start.append(cov[0])
                cov_finsh.append(cov[-1])
                ck_kernels.append(kernel)
                colors.append(color)

    spice.furnsh(mk)
    date_format = 'UTC'

    start_dt = []
    for element in cov_start:
        start_dt.append(et_to_datetime(element, date_format))

    finish_dt = []
    for element in cov_finsh:
        finish_dt.append(et_to_datetime(element, date_format))

    fig = go.Figure()

    for i in range(len(start_dt)):

        middle_dt = et_to_datetime(cov_start[i] + (cov_finsh[i] - cov_start[i])/2)

        fig.add_trace(
            go.Scatter(x=[start_dt[i], finish_dt[i]], y=[height, height], mode='lines',
            name=ck_kernels[i], line=dict(width=20, color=colors[i])))#, fill="toself",
                       #fillcolor=colors[i], name=ck_kernels[i], line=dict(color='rgba(0,0,0,0)'), marker=dict(opacity=0)))
        fig.add_trace(
            go.Scatter(x=[middle_dt], y=[height],
                       mode='text',text=ck_kernels[i],textposition="middle center"))

        height += 1

    title = "CK Kernels Coverage"
    if 'ops' in mk.lower():
        title += ' - OPS Metakernel'
    elif 'plan' in mk.lower():
        title += ' - PLAN Metakernel'

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        margin=dict(l=20, r=20, t=27, b=20),
        font=dict(size=10, color="Black"),
        showlegend=False,
        yaxis=dict(showticklabels=False),
        legend=dict(yanchor="top", y=-0.1, xanchor="left", x=0)
    )

    fig.show()


def spk_coverage_timeline(mk, sc = 'JUICE', height=0):

    cov_start = []
    cov_finish = []
    kernels = []

    with open(mk, 'r') as f:
        for line in f:
            if '/spk/' in line and 'prelaunch' not in line:
                kernels.append(line.split('/spk/')[-1].strip().split("'")[0])
            if 'PATH_VALUES' in line and '=' in line:
                path = line.split("'")[1] + '/spk/'

    kernels = list(reversed(kernels))
    spk_kernels = []
    colors = []

    for kernel in kernels:
        cov = cov_spk_ker(path+kernel, sc.upper(), support_ker=mk,
                            time_format='TDB')
        if cov:
            color = "chartreuse"
            if 'orb' in kernel:
                color = 'orange'
            elif 'crema' in kernel:
                color = 'lawngreen'
            cov_start.append(cov[0][0])
            cov_finish.append(cov[0][-1])
            spk_kernels.append(kernel)
            colors.append(color)

    spice.furnsh(mk)
    date_format = 'UTC'
    start_dt =[]
    finish_dt =[]
    for element in cov_start:
        start_dt.append(et_to_datetime(element, date_format))
    for element in cov_finish:
        finish_dt.append(et_to_datetime(element, date_format))

    fig = go.Figure()

    for i in range(len(start_dt)):

        middle_dt = et_to_datetime(cov_start[i] + (cov_finish[i] - cov_start[i])/2)

        fig.add_trace(
            go.Scatter(x=[start_dt[i], finish_dt[i]], y=[height, height], mode='lines',
            name=spk_kernels[i], line=dict(width=20, color=colors[i])))
        fig.add_trace(
            go.Scatter(x=[middle_dt], y=[height],
                       mode='text',text=spk_kernels[i],textposition="middle center"))

        height += 1

    title = "SPK Kernels Coverage"
    if 'ops' in mk.lower():
        title += ' - OPS Metakernel'
    elif 'plan' in mk.lower():
        title += ' - PLAN Metakernel'

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        margin=dict(l=20, r=20, t=27, b=20),
        font=dict(size=10, color="Black"),
        showlegend=False,
        yaxis=dict(showticklabels=False),
        legend=dict(yanchor="top", y=-0.1, xanchor="left", x=0)
    )

    fig.show()
