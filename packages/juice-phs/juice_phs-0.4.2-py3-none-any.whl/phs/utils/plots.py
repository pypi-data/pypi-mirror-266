import pandas as pd
import json

import spiceypy
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from .time import et_to_datetime

load_dotenv()
CONF_DIR = os.getenv('CONF_REPO')

def plot_timeline_observations_background(fig, opl_csv):
    """Plot observations in the background by color."""
    # each observation has a different color
    i = 0
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    df = pd.read_csv(opl_csv, names=["name","t_start","t_end","subgroup","source"])
    df = df[~df.iloc[:, 0].str.startswith('#')]

    for index, row in df.iterrows():
        fig.add_vrect(x0=row['t_start'], x1=row['t_end'],
                      annotation_text=row['subgroup'], annotation_position="bottom left",
                      fillcolor=colors[i], annotation_font_color=colors[i],
                      opacity=0.15, line_width=0)

        i += 1
        if i == len(colors):
            i = 0
    return


def plot_timeline_observations_gantt(fig, opl_csv, height=10, fillcolor='red'):
    """Plot observations in the background by color."""
    # each observation has a different color

    df = pd.read_csv(opl_csv, names=["name","t_start","t_end","subgroup","source"])
    df = df[~df.iloc[:, 0].str.startswith('#')]

    for index, row in df.iterrows():
        fig.add_trace(
            go.Scatter(x=[row['t_start'], row['t_end'], row['t_end'], row['t_start']], y=[height, height, height+10, height+10], fill="toself",
                       fillcolor=fillcolor, name=row['subgroup'], line=dict(color='rgba(0,0,0,0)'), marker=dict(opacity=0)))
    return


def plot_events_background(fig, event_time_intervals, event_name, color='green'):
    """Plot observations in the background by color."""
    # each observation has a different color
    for interval in event_time_intervals:
        fig.add_vrect(x0=interval[0], x1=interval[-1],
                      annotation_text=event_name, annotation_position="bottom left",
                      fillcolor=color, annotation_font_color=color,
                      opacity=0.15, line_width=0)
    return


def osve_errors(log_file):
    """Plot observations in the background by color."""
    # each observation has a different color
    with open(log_file, 'r') as file:
        data = json.load(file)

    # Filter and display entries with severity "error"
    error_entries = [entry for entry in data if (entry["severity"] == "ERROR" and entry["time"])]
    error_texts = [f'{entry["time"]:<{21}} {entry["text"]}' for entry in error_entries]

    for error_text in error_texts:
        print(error_text)
    return


def osve_mga_warnings(log_file, time_interval):
    """Plot observations in the background by color."""
    # each observation has a different color
    with open(log_file, 'r') as file:
        data = json.load(file)

    interval_start = spiceypy.utc2et(time_interval[0])
    interval_end = spiceypy.utc2et(time_interval[-1])

    # Filter and display entries with severity "error"
    error_entries = [entry for entry in data if ("MGA" in entry["text"])]
    error_mga_entries = []
    for entry in error_entries:
        if entry["time"]:
            entry_time = spiceypy.utc2et(entry["time"])
            if entry_time <= interval_end and entry_time >= interval_start:
                error_mga_entries.append(entry)

    error_texts = [f'{entry["time"]:<{21}} {entry["text"]}' for entry in error_mga_entries]

    for error_text in error_texts:
        print(error_text)
    return


def plot_timeline_osve_errors(fig, log_file, verbose=False):
    """Plot observations in the background by color."""
    # each observation has a different color
    with open(log_file, 'r') as file:
        data = json.load(file)

    # Filter and display entries with severity "error"
    error_entries = [entry for entry in data if (entry["severity"] == "ERROR" and entry["time"])]
    error_texts = [f'{entry["time"]:<{21}} {entry["text"]}' for entry in error_entries]

    for error_text in error_texts:
        if verbose:
            print(error_text)
        fig.add_vline(x=error_text.split()[0], line_width=3, line_color="red")
    return


def plot_timeline_sht_events(fig, events):
    """Plot observations in the background by color."""
    # each observation has a different color

    df = pd.DataFrame(events)

    for index, row in df.iterrows():
        fig.add_vrect(x0=row['start'], x1=row['end'],
                      annotation_text=row['name'], annotation_position="bottom left",
                      fillcolor='coral', annotation_font_color='orange',
                      opacity=0.15, line_width=0)

    return


def plot_timeline_intervals_gantt(fig, intervals, name="MGA Maksed", fillcolor = "blue", height=50):
    """Plot observations in the background by color."""
    # each observation has a different color
    for interval in intervals:
        fig.add_trace(
            go.Scatter(x=[interval[0], interval[1], interval[1], interval[0]], y=[height, height, height+10, height+10], fill="toself",
                       fillcolor=fillcolor, opacity=0.6,
                       name=name, line=dict(color='rgba(0,0,0,0)'), marker=dict(opacity=0)))
    return
