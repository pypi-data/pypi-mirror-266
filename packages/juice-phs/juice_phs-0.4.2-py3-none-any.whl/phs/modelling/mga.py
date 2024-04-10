import spiceypy as spice
from dotenv import load_dotenv
import os

from datetime import datetime

from phs.geometry.derived import earth_direction

import numpy as np

load_dotenv()
CONF_DIR = os.getenv('CONF_REPO')

## IDL GEOPIPELINE ROUTINES

def format_seconds(seconds):
    hours = int(seconds) // 3600
    minutes = int(seconds) % 3600 // 60
    remaining_seconds = int(seconds) % 60

    return f'{hours:02d}:{minutes:02d}:{remaining_seconds:02d}'


def read_mga_masking(mask_file_name='FDDB_V6_mga_masking.csv'):
    """
    This routine loads and reads the masking of the MGA (directions resulting in the
    beam intersecting different SC structure or instruments elements)
    as provided by Airbus - (attachment of JUI-ADST-SYS-TN-000563, issue 2, 07/06/2021).

    Original version: NA, January 2022.

    Input: None - the routine grabs the CSV version of the masking from the conf repository.

    Output: the MGA mask data, with a flag 0 (no intersection) or 1 (intersection) for the
    boom angle (-160/+20, sampling 10 deg) and dish elevation angle (0-359, sampling 1 deg).
    """

    # Define file paths and names
    try:
        mga_mask_file = f'{CONF_DIR}/external/data/fd/common/{mask_file_name}'
    except:
        mga_mask_file = f'{os.path.dirname(os.path.abspath(__file__))}/../data/{mask_file_name}'

        # Open and read the file
    with open(mga_mask_file, 'r') as file:
        lines = file.readlines()
        n_lines = len(lines)

    # Define constants
    MGA_MASK_ELEVATION_MIN = -127  # deg
    MGA_MASK_ELEVATION_MAX = 230  # deg
    MGA_MASK_ELEVATION_STEP = 1   # deg
    MGA_MASK_AZIMUTH_MIN = -160   # deg
    MGA_MASK_AZIMUTH_MAX = 20    # deg
    MGA_MASK_AZIMUTH_STEP = 1     # deg

    # Create azimuth and elevation arrays
    azimuth_vals = np.arange(MGA_MASK_AZIMUTH_MIN, MGA_MASK_AZIMUTH_MAX + 1, MGA_MASK_AZIMUTH_STEP)
    elev_vals = np.arange(MGA_MASK_ELEVATION_MIN, MGA_MASK_ELEVATION_MAX + 1, MGA_MASK_ELEVATION_STEP)
    n_azi = len(azimuth_vals)
    n_elev = len(elev_vals)

    # Initialize mga_mask_data as a NumPy integer array
    mga_mask_data = np.zeros((n_azi, n_elev), dtype=int)

    # Search for the line where the mask data starts
    for line in lines:
        if 'MGA_MASK_AZIMUTH_STEP' in line:
            break

    # Read and parse the data
    for k in range(n_azi):
        line = lines.pop(12)
        tmp = line.strip().split(';')
        mga_mask_data[k, :] = [int(val) for val in tmp[3:-1]]

    # Create a dictionary for mga_mask
    mga_mask = {
        'mask_description': mask_file_name,
        'mga_azimuth': azimuth_vals.tolist(),
        'mga_elevation': elev_vals.tolist(),
        'mga_mask_data': mga_mask_data.tolist()
    }


    return mga_mask


def get_mga_mask_flag(mga_mask, mga_azi, mga_elev):
    """
    Returns the MGA flag (interception of SC structure or instruments that should not be illuminated) for
    given azimuth and elevation values of the MGA - as defined in FDDB.

    :param mga_mask: Dictionary containing MGA mask data with keys 'mga_azimuth', 'mga_elevation', and 'mga_mask_data'.
    :param mga_azi: Array of MGA azimuth values.
    :param mga_elev: Array of MGA elevation values.
    :return: Intersection flag for each azimuth and elevation combination.
    """
    # Find the indices of azimuth and elevation values in the MGA mask data
    ind_boom = int(np.searchsorted(mga_mask['mga_azimuth'], mga_azi)) - 1
    ind_dish = int(np.searchsorted(mga_mask['mga_elevation'], mga_elev)) - 1

    # Get the intersection flag from the MGA mask data
    intersection_flag = mga_mask['mga_mask_data'][ind_boom][ind_dish]

    return intersection_flag


def get_mga_azimuth_elevation_for_earth_direction(utc_list, plot=False):
    """
    This routine returns the MGA azimuth and elevation angles required for a set of SC to Earth vectors
    as well as whether the MGA beam is masked by SC or instrument elements.

    All angle descriptions and masking data are aligned with the AIRBUS conventions as described in JUI-ADST-SYS-TN-000563.

    INPUT: Array of SC to Earth vectors expressed in Cartesian coordinates in the SC frame [n,3]

    OUTPUT: MGA azimuth and elevation angle following the AIRBUS conventions as described in Fig. 3.2-B, mask flag for each Earth direction
    """
    earth_vec_directions = [earth_direction(utc) for utc in utc_list]
    n_directions = len(earth_vec_directions)

    mga_azi = np.full(n_directions, -999.0)  # Default value is -999 if no valid position is found
    mga_elev = np.full(n_directions, -999.0)
    mask_flag = np.full(n_directions, 0)

    sc_zaxis = np.array([0.0, 0.0, 1.0])  # in JUICE_SPACECRAFT FRAME

    # Read the MGA masking data from a file or source
    mga_mask = read_mga_masking()

    for i in range(n_directions):
        sc2earth_vect = earth_vec_directions[i]
        # The boom shall be perpendicular to the Earth direction projected into the XY plane
        sc2earth_vect_proj = np.array([sc2earth_vect[0], sc2earth_vect[1], 0.0])

        # Rotate the SC2Earth vect by 90 deg around Z
        boom_vect_1 = spice.vrotv(sc2earth_vect_proj, sc_zaxis, np.pi / 2.0)
        boom_vect_2 = spice.vrotv(sc2earth_vect_proj, sc_zaxis, -np.pi / 2.0)

        # Get the corresponding azimuth values using Airbus conventions
        rad, rec1, lat1 = spice.reclat(boom_vect_1)
        rrad, rec2, lat2 = spice.reclat(boom_vect_2)

        mga_azi_1 = rec1 * spice.dpr() + 90.0  # such that rec=-90 (-Y axis) is the 0 position
        mga_azi_2 = rec2 * spice.dpr() + 90.0

        if mga_azi_1 > 180.0:
            mga_azi_1 -= 360.0
        if mga_azi_2 > 180.0:
            mga_azi_2 -= 360.0

        boom_azi_min = -160.0
        boom_azi_max = 20.0

        # Take the value within acceptable range and keep the resulting boom vect for later use.
        if boom_azi_min <= mga_azi_1 <= boom_azi_max:
            mga_azi[i] = mga_azi_1
            boom_vect = boom_vect_1
        elif boom_azi_min <= mga_azi_2 <= boom_azi_max:
            mga_azi[i] = mga_azi_2
            boom_vect = boom_vect_2

        # if we have found a proper boom orientation, look for the dish elevation
        if mga_azi[i] > -999.0:

            # The MGA 0 deg elevation vector is the vector product between the boom vector and +Z
            mga_zero_elevation_vect = spice.vcrss(boom_vect, [0.0, 0.0, 1.0])

            # At this point, by construction, the SC2Earth vector is in the plane defined by the
            # mga 0deg elevation vector and +Z
            # We first find the angular separation between the SC2Earth vector and the mga_0_elevation_vect
            mga_elevation_tmp = spice.vsep(mga_zero_elevation_vect, sc2earth_vect) * spice.dpr()

            # And we have to convert this value to the Airbus MGA 'elevation' angle
            sign = 1  # Default
            if sc2earth_vect[2] < 0:
                sign = -1

            mga_elevation_tmp = mga_elevation_tmp * sign
            mga_elev[i] = mga_elevation_tmp

            # Now apply the masking (aligned with the FDDB)
            mask_flag[i] = get_mga_mask_flag(mga_mask, mga_azi[i],  mga_elev[i])

    if plot:
        plot_mga_masking(mga_mask, mga_azi, mga_elev)

    return mga_azi, mga_elev, mask_flag


def find_mga_masked_intervals(utc_list, boolean_values, verbose=True):
    if len(utc_list) != len(boolean_values):
        raise ValueError("Input lists must have the same length")

    true_intervals = []
    start_time = None

    for i in range(len(utc_list)):
        if boolean_values[i] == 1:
            if start_time is None:
                start_time = datetime.strptime(utc_list[i], "%Y-%m-%dT%H:%M:%S")
        elif start_time:
            end_time = datetime.strptime(utc_list[i], "%Y-%m-%dT%H:%M:%S")
            true_intervals.append((start_time.strftime("%Y-%m-%dT%H:%M:%S"), end_time.strftime("%Y-%m-%dT%H:%M:%S")))
            start_time = None

    # Check if the last interval continues to the end
    if start_time is not None:
        end_time = datetime.strptime(utc_list[-1], "%Y-%m-%dT%H:%M:%S")
        true_intervals.append((start_time.strftime("%Y-%m-%dT%H:%M:%S"), end_time.strftime("%Y-%m-%dT%H:%M:%S")))

    if verbose:
        total_time = spice.utc2et(utc_list[-1]) - spice.utc2et(utc_list[0])
        accumulated_time = 0
        for interval in true_intervals:
            print(f'MGA Masking Violation: {interval[0]} - {interval[1]}')
            accumulated_time += spice.utc2et(interval[1]) - spice.utc2et(interval[0])


        comms_duration = total_time-accumulated_time

        print(f'MGA Block Duration:  {format_seconds(total_time)}')
        print(f'MGA Masked Duration: {format_seconds(accumulated_time)}')
        print(f'MGA Comms Duration:  {format_seconds(comms_duration)}')

        if comms_duration < 4*60*60:
            print(f'MGA Communications Minimum Duration not reached.')

    return true_intervals


def plot_mga_masking(mga_mask, mga_azi, mga_elev):
    # Create a DataFrame for the mga_mask_data
    import plotly.graph_objects as go

    mga_mask_data = [[row[i] for row in mga_mask['mga_mask_data']] for i in range(len(mga_mask['mga_mask_data']))]
    numeric_variable = np.linspace(0, len(mga_azi)-1, len(mga_azi))
    layout = go.Layout(title='MGA Masking', yaxis=dict(title='Azimuth (degrees)'),
                       xaxis=dict(title='Elevation (degrees)'))
    contour = go.Contour(x=mga_mask['mga_azimuth'], y=mga_mask['mga_elevation'], z=mga_mask_data,
                         showscale=False, colorscale=[[0, 'white'], [1, 'lightgrey']])
    trace1 = go.Scatter(x=mga_azi, y=mga_elev,
                        mode='markers',
                        marker=dict(
                        color=numeric_variable,
                        colorscale='bluered'))

    fig = go.Figure(data=[contour, trace1], layout=layout)

    # Invert the elevation axis to match common conventions
    fig.update_yaxes(autorange='reversed')

    fig.update_layout(
        margin=dict(l=20, r=20, t=27, b=20),
        font=dict(size=10, color="Black"),

    )

    # Show the plot
    fig.show()
