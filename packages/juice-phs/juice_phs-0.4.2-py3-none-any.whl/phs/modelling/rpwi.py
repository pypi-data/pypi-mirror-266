import plotly.graph_objects as go
import spiceypy as spice

from phs.geometry.ray_tracing import plot_shadow_timeline
from phs.utils.output import write_csv


def langmuir_probe_illumination(utc_start, utc_end, resolution=False, plot=False, output=False):
    """
    Calculate Langmuir probe illumination percentages over a specified time range.

    Parameters
    ----------
    utc_start : str
        Start UTC time format.
    utc_end : str
        End UTC time format.
    plot : bool, optional
        Toggle to display the illumination plot (default is False).

    Returns
    -------
    list
        List of sampled UTC times.
    list
        Percentage of surface illumination for Langmuir Probe 1.
    list
        Percentage of surface illumination for Langmuir Probe 2.
    list
        Percentage of surface illumination for Langmuir Probe 3.
    list
        Percentage of surface illumination for Langmuir Probe 4.
    """
    et_start = spice.utc2et(utc_start)
    et_end = spice.utc2et(utc_end)

    if resolution:
        samples =  (et_end - et_start)//resolution
    else:
        samples = 1000
        resolution = (et_end - et_start)/samples
    utcs, lp1_shadow = plot_shadow_timeline(utc0=utc_start, utcf=utc_end, n=samples, observer='JUICE_RPWI_LP1',
                                            observerframe='JUICE_RPWI_LP1')
    utcs, lp2_shadow = plot_shadow_timeline(utc0=utc_start, utcf=utc_end, n=samples, observer='JUICE_RPWI_LP2',
                                            observerframe='JUICE_RPWI_LP2')
    utcs, lp3_shadow = plot_shadow_timeline(utc0=utc_start, utcf=utc_end, n=samples, observer='JUICE_RPWI_LP3',
                                            observerframe='JUICE_RPWI_LP3')
    utcs, lp4_shadow = plot_shadow_timeline(utc0=utc_start, utcf=utc_end, n=samples, observer='JUICE_RPWI_LP4',
                                            observerframe='JUICE_RPWI_LP4')

    if plot:
        fig = go.Figure()
        fig.add_traces(go.Scatter(x=utcs, y=lp1_shadow, mode='lines', name='LP1 % surface illumination'))
        fig.add_traces(go.Scatter(x=utcs, y=lp2_shadow, mode='lines', name='LP2 % surface illumination'))
        fig.add_traces(go.Scatter(x=utcs, y=lp3_shadow, mode='lines', name='LP3 % surface illumination'))
        fig.add_traces(go.Scatter(x=utcs, y=lp4_shadow, mode='lines', name='LP4 % surface illumination'))

        fig.update_layout(
            title='RPWI Langmuir Probe Illumination',
            yaxis_title="Percentage illuminated (%)",
            xaxis_title="Date",
            margin=dict(l=20, r=20, t=27, b=20),
            font=dict(size=10, color="Black"),
            showlegend=True,
            legend=dict(yanchor="top", y=-0.1, xanchor="left", x=0)
        )

        fig.show()

    if output:
        write_csv(["Date","LP 1 Illumination (%)","LP 2 Illumination (%)","LP 3 Illumination (%)","LP 4 Illumination (%)"],
                  [utcs, lp1_shadow, lp2_shadow, lp3_shadow, lp4_shadow], output, 'RPWI Langmuir Probe Illumination', resolution)

    return utcs, lp1_shadow, lp2_shadow, lp3_shadow, lp4_shadow