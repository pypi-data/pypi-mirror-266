import spiceypy as spice
import plotly.graph_objects as go
from tqdm import tqdm

from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


def obstruction_targets(observer=''):
    """
    Generate a list of celestial bodies and spacecraft that can potentially obstruct observations.

    Parameters
    ----------
    observer : str, optional
        The observer's reference frame (default is '').

    Returns
    -------
    list
        List of potential obstruction targets containing body names, IDs, frames, methods, and obstruction colors.
    """
    targets = [
        # Body, Id, Fixed_frame, Method, Color
        ['EARTH', 399, 'IAU_EARTH', 'ELLIPSOID', 0.5],
        ['MOON', 301, 'IAU_MOON', 'ELLIPSOID', 0.5],
        ['VENUS', 299, 'IAU_VENUS', 'ELLIPSOID', 0.5],
        ['JUPITER', 599, 'IAU_JUPITER', 'ELLIPSOID', 0.5],
        ['GANYMEDE', 503, 'IAU_GANYMEDE', 'ELLIPSOID', 0.5],
        ['EUROPA', 502, 'IAU_EUROPA', 'ELLIPSOID', 0.5],
        ['CALLISTO', 504, 'IAU_CALLISTO', 'ELLIPSOID', 0.5],
        ['JUICE_SPACECRAFT', -28000, 'JUICE_SPACECRAFT', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_SA+Y', -28011, 'JUICE_SA+Y', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_SA-Y', -28015, 'JUICE_SA-Y', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_MGA', -28048, 'JUICE_MGA', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RIME+X', -28601, 'JUICE_RIME+X', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RIME-X', -28602, 'JUICE_RIME-X', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_LPB1', -28701, 'JUICE_RPWI_LPB1', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_LPB2', -28711, 'JUICE_RPWI_LPB2', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_LPB3', -28721, 'JUICE_RPWI_LPB3', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_LPB4', -28731, 'JUICE_RPWI_LPB4', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_RWI', -28740, 'JUICE_RPWI_RWI', 'DSK/UNPRIORITIZED', 1],
        ['JUICE_RPWI_SCM', -28750, 'JUICE_RPWI_SCM', 'DSK/UNPRIORITIZED', 1]
    ]
        #['JUICE_STR-OH1', -28061, 'JUICE_STR-OH1', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_STR-OH2', -28062, 'JUICE_STR-OH2', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_STR-OH3', -28063, 'JUICE_STR-OH3', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_JMC-1', -28081, 'JUICE_JMC-1', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_JMC-2', -28082, 'JUICE_JMC-2', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_GALA', -28100, 'JUICE_GALA', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_JANUS', -28200, 'JUICE_JANUS', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_MAJIS', -28400, 'JUICE_MAJIS_BASE', 'DSK/UNPRIORITIZED', 1],

        #['JUICE_PEP_JDC', -28510, 'JUICE_PEP_JDC', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_PEP_JNA', -28520, 'JUICE_PEP_JNA', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_PEP_NIM', -28530, 'JUICE_PEP_NIM', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_PEP_JEI', -28540, 'JUICE_PEP_JEI', 'DSK/UNPRIORITIZED', 1],
        #['JUICE_PEP_JENI', -28560, 'JUICE_PEP_JENI', 'DSK/UNPRIORITIZED', 1],

        #['JUICE_SWI_FULL', -28800, 'JUICE_SWI_BASE', 'DSK/UNPRIORITIZED', 1],


    for target in targets:
        if target[0] == observer:
            targets.remove(target)

    return targets


def intersection(ray, target, targetframe, observer, observerframe, et, method):
    """
    Determine if a ray intersects a specified target.

    Parameters
    ----------
    ray : list
        Ray defined by its direction.
    target : str
        Name of the target body.
    targetframe : str
        Target body's reference frame.
    observer : str
        Observer's reference frame.
    observerframe : str
        Observer's reference frame.
    et : float
        Ephemeris Time (ET) in seconds past J2000.
    method : str
        Method for the intersection calculation.

    Returns
    -------
    bool
        True if the ray intersects the target, False otherwise.
    """
    try:
        spice.sincpt(method, target, et, targetframe, 'NONE', observer, observerframe, ray)[0]
    except:
        return False
    return True


def plot_obstruction(utc, observer, observerframe, plot=False):
    """
    Plot the obstruction map for a specified observer at a given time.

    Parameters
    ----------
    utc : str
        UTC time format.
    observer : str
        Observer's reference frame.
    observerframe : str
        Observer's reference frame.
    plot : bool, optional
        Toggle to display the plot (default is False).

    Returns
    -------
    float
        Percentage of obstruction within the observer's FOV.
    """
    et = spice.utc2et(utc)
    lat = np.linspace(np.pi / 2, -np.pi / 2, 181)
    lon = np.linspace(0, 2 * np.pi, 361)
    map = np.zeros((181, 361))

    targets = obstruction_targets(observer)
    print(targets)

    for i in tqdm(range(0, len(lat))):
        for j in range(0, len(lon)):
            ray = spice.latrec(1, lon[j], lat[i])
            incidence = np.rad2deg(spice.vsep(ray, spice.spkpos('SUN', et, observerframe, 'NONE', observer)[0]))
            if incidence > 90:
                map[i, j] = 0.8
            for target in targets:
                if intersection(ray=ray,
                                target=target[0], targetframe=target[2],
                                observer=observer, observerframe=observerframe,
                                et=et, method=target[3]):
                    map[i, j] = target[4]
    obstruction = np.sum(map[map > 0] * 0 + 1) / map.size * 100
    print('Percentage of obstruction: ', obstruction)

    if plot:
        map = np.flip(np.transpose(np.flip(map, 0)), 0)
        contour = go.Contour(z=map, colorscale='Viridis', showscale=False)

        # Create the layout
        layout = go.Layout(
            xaxis=dict(title='Pixel Samples'),
            yaxis=dict(title='Pixel Lines'),
            title=f'{observer} Surface Obstruction',
            margin=dict(l=20, r=20, t=27, b=20),
            font=dict(
                size=10,  # Set the font size here
                color="Black"
            ))

        # Create the figure
        fig = go.Figure(data=[contour], layout=layout)
        # Show the Plotly graphic object (you can also save it to an HTML file)
        fig.show()

    return obstruction


def plot_fov_obstruction(utc, camera, pixel_lines='', pixel_samples='', observer='', plot=False):
    """
    Plot the Field of View (FOV) obstruction map for a specified camera at a given time.

    Parameters
    ----------
    utc : str
        UTC time format.
    camera : str
        Camera's name.
    pixel_lines : int, optional
        Number of pixel lines (default is '').
    pixel_samples : int, optional
        Number of pixel samples (default is '').
    observer : str
        Observer's reference frame.
    plot : bool, optional
        Toggle to display the plot (default is False).

    Returns
    -------
    float
        Percentage of obstruction within the camera's FOV.
    """
    et = spice.utc2et(utc)

    targets = obstruction_targets(observer)
    if not observer:
        observer = camera

    #
    # We retrieve the camera information using GETFOV. More info available:
    #
    camera_name = camera
    camera_id = spice.bodn2c(camera_name)
    (shape, frame, bsight, vectors, bounds) = spice.getfov(camera_id, 100)
    print('Inst frame:  ', frame)
    print('Inst bsight: ', bsight)
    print('Inst shape:  ', shape)
    print('Targ obstr:  ', [target[0] for target in targets])
    #
    # We check if the resolution of the camera has been provided as an input
    # if not we try to obtain the resolution of the camera from the IK
    #
    if not pixel_lines or not pixel_samples:
        try:
            pixel_samples = int(spice.gdpool('INS' + str(camera_id) + '_PIXEL_SAMPLES', 0, 1))
            pixel_lines = int(spice.gdpool('INS' + str(camera_id) + '_PIXEL_LINES', 0, 1))
        except:
            pass
            print("PIXEL_SAMPLES and/or PIXEL_LINES not defined for "
                  "{}".format(camera))
            return

    #
    # We generate a matrix using the resolution of the framing camera as the
    # dimensions of the matrix
    #
    nx, ny = (pixel_samples, pixel_lines)
    x = np.linspace(bounds[0][0], bounds[2][0], nx)
    y = np.linspace(bounds[0][1], bounds[2][1], ny)

    #
    # We define the matrices that will be used as outputs and the
    #
    map = np.zeros((nx, ny))

    for i in tqdm(range(0, len(x))):
        for j in range(0, len(y)):

            #
            # List of pixel's boresight
            #
            ibsight = [x[i], y[j], bounds[0][2]]
            for target in targets:
                if intersection(ray=ibsight,
                                target=target[0], targetframe=target[2],
                                observer=observer, observerframe=frame,
                                et=et, method=target[3]):
                    map[i, j] = target[4]
    obstruction = np.sum(map[map > 0] * 0 + 1) / map.size * 100
    print('Percentage of obstruction: ', obstruction)

    if plot:
        map = np.flip(np.transpose(np.flip(map, 0)), 0)
        contour = go.Contour(z=map, colorscale='Viridis', showscale=False)

        # Create the layout
        layout = go.Layout(
            xaxis=dict(title='Pixel Samples'),
            yaxis=dict(title='Pixel Lines'),
            title=f'{camera} FOV Obstruction',
            margin=dict(l=20, r=20, t=27, b=20),
            font=dict(
                size=10,  # Set the font size here
                color="Black"
            ))

        # Create the figure
        fig = go.Figure(data=[contour], layout=layout)
        # Show the Plotly graphic object (you can also save it to an HTML file)
        fig.show()

    return obstruction


def plot_shadow(utc, observer, observerframe):
    """
    Calculate the percentage of shadowed area within the FOV of an observer.

    Parameters
    ----------
    utc : str or float
        UTC time format or Ephemeris Time (ET) in seconds past J2000.
    ny : int
        Number of latitude samples.
    nx : int
        Number of longitude samples.
    observer : str
        Observer's reference frame.
    observerframe : str
        Observer's reference frame.

    Returns
    -------
    float
        Percentage of shadowed area within the observer's FOV.
    """
    et = spice.utc2et(utc)
    targets = obstruction_targets(observer)

    lat = np.linspace(np.pi / 2, -np.pi / 2, 181)
    lon = np.linspace(0, 2 * np.pi, 361)
    map = np.zeros((181, 361))

    sundir = spice.spkpos('SUN', et, observerframe, 'NONE', observer)[0]

    for i in tqdm(range(0, len(lat))):
        for j in range(0, len(lon)):
            ray = spice.latrec(0.00005, lon[j], lat[i])
            incidence = np.rad2deg(spice.vsep(ray, sundir))
            if incidence > 90:
                map[i, j] = 0.8
            else:
                for target in targets:
                    if target[3] == 'ELLIPSOID':
                        if intersection(ray=sundir,
                                        target=target[0], targetframe=target[2],
                                        observer=observer, observerframe=observerframe,
                                        et=et, method=target[3]):
                            map[i, j] = target[4]
                    else:
                        r0 = ray
                        r_opt = spice.spkpos(observer, et, target[2], 'NONE', target[0])[0]
                        M = spice.pxform(observerframe, target[2], et)
                        r = spice.mxv(M, r0) + r_opt
                        d = spice.mxv(M, sundir / np.linalg.norm(sundir))

                        xarray, flag = spice.dskxv(False, target[0], [target[1]], et, target[2],
                                                   [r], [d])
                        if flag == True:
                            map[i, j] = target[4]
    plt.imshow(map)
    plt.grid()
    plt.show()
    return


def plot_shadow_flag(utc, ny, nx, observer, observerframe):
    try:
        et = spice.utc2et(utc)
    except:
        et = utc

    targets = obstruction_targets(observer)
    lat = np.linspace(np.pi / 2, -np.pi / 2, ny)
    lon = np.linspace(0, 2 * np.pi, nx)
    map = np.zeros((ny, nx))

    sundir = spice.spkpos('SUN', et, observerframe, 'NONE', observer)[0]

    for i in (range(0, len(lat))):
        for j in range(0, len(lon)):
            ray = spice.latrec(0.00005, lon[j], lat[i])
            incidence = np.rad2deg(spice.vsep(ray, sundir))
            if incidence < 90:
                map[i, j] = 1.0
    for target in targets:
        if intersection(ray=sundir,
                        target=target[0], targetframe=target[2],
                        observer=observer, observerframe=observerframe,
                        et=et, method=target[3]):
            map *= 0
    return np.sum(map) / (ny * nx) * 100


def plot_shadow_timeline(utc0, utcf, n, observer, observerframe, plot=False):
    """
    Plot the timeline of surface illumination percentage over a specified period.

    Parameters
    ----------
    utc0 : str
        Start UTC time format.
    utcf : str
        End UTC time format.
    n : int
        Number of time samples.
    observer : str
        Observer's reference frame.
    observerframe : str
        Observer's reference frame.
    plot : bool, optional
        Toggle to display the plot (default is False).

    Returns
    -------
    list
        List of UTC times sampled.
    list
        List of percentage values of surface illumination corresponding to the sampled times.
    """
    out = []
    times = np.linspace(spice.utc2et(utc0), spice.utc2et(utcf), n)
    for et in tqdm(times):
        out.append(plot_shadow_flag(et, ny=18, nx=36, observer=observer, observerframe=observerframe))
    utcs = [datetime.strptime(spice.et2utc(i, 'ISOC', 0), '%Y-%m-%dT%H:%M:%S') for i in times]

    if plot:
        plt.plot(utcs, out)
        plt.grid()
        plt.title('Percentage of surface illumination')
        plt.xlabel('UTC [-]')
        plt.ylabel('Percentage illuminated [%]')
        plt.show()
    return utcs, out