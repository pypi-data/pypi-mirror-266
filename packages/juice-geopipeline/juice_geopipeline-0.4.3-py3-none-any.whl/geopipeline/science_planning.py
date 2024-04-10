import sys

import spiceypy as spice
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from pprint import pprint

from .setup import conf_path, geopipeline_path
from .geometry.finder import tour_flip_zaxis, transits

CONF_PATH = conf_path()
GEOPIPELINE_PATH = geopipeline_path()


def jupiter_tour_flip_zaxis_windows(utc_start='', utc_end='', crema_version='', mission_phase='',
                                    duration=3600, mission_timeline_event_file='', output='', verbose=False,
                                    meta_kernel='', kclear=True):
    """
     Jupiter Tour +Z axis flip windows generation.

     This function generates the flip windows during the Jupiter tour between the specified
     UTC start and end times or Mission Phase.

     Parameters:
     -----------
     utc_start : str, optional
         Start time in UTC format.
     utc_end : str, optional
         End time in UTC format.
     crema_version : str, optional
         JUICE Crema (trajectory) version
     duration : int, optional
         Duration of the segment in seconds (default: 3600).
     mission_timeline_event_file : str, optional
         Path to the mission timeline event file (default: '').
     output : str, optional
         Output file path (default: '').
     verbose : bool, optional
         If True, print detailed information (default: False).
     meta_kernel : str, optional
         Path to the SPICE meta-kernel file (default: '').

     Returns:
     --------
     list[list[str]]
         A list of flip segments represented as [start_time, end_time] in UTC format.

     Note:
     -----
     If `meta_kernel` is provided, it loads the kernel using SPICE furnsh. Remember to call spice.kclear()
     after using the function to clear loaded kernels if necessary.
     """

    # Derive the Mission timeline event file from the Crema
    if not mission_timeline_event_file:
        mission_timeline_event_file = f'{CONF_PATH}/internal/geopipeline/output/Crema_{crema_version}/' \
                                      f'mission_timeline_event_file_{crema_version}.csv'

    if not meta_kernel:
        meta_kernel = f'{GEOPIPELINE_PATH}/cfg_files/Generic_meta_kernel_crema_{crema_version}.cfg'
    spice.furnsh(meta_kernel)

    if not utc_start and not utc_end:
        (utc_start, utc_end) = get_mission_phase_times(crema_version, mission_phase)

    riswin, rislis = tour_flip_zaxis(utc_start, utc_end)

    segments_start =  [spice.et2utc((interval[0] - duration/2),'ISOC', 0, 80) for interval in rislis]
    segments_stop  =  [spice.et2utc((interval[1] + duration/2),'ISOC', 0, 80) for interval in rislis]

    segments = [[segments_start[i], segments_stop[i]] for i in range(len(segments_start))]
    if verbose:
        print('FLIP_ZAXIS windows UTC start and end:')
        pprint(segments)

    if mission_timeline_event_file:
        df = pd.read_csv(mission_timeline_event_file, header=0, sep=',')

        for segment in segments:
           start_row = {'#Event name': 'FLIP_ZAXIS_START', ' event time [utc]': segment[0]+'Z'}
           end_row = {'#Event name': 'FLIP_ZAXIS_END', ' event time [utc]': segment[1]+'Z'}

           df = pd.concat([df, pd.DataFrame([start_row])], ignore_index=True)
           df = pd.concat([df, pd.DataFrame([end_row])], ignore_index=True)

        df = df.sort_values(by=' event time [utc]')

        if not output:
            output = mission_timeline_event_file

        df.to_csv(output, index=False)

        if kclear:
            spice.kclear()

    return segments


def read_mission_phase_file(crema_version='', file_path=''):
    """
    Read the mission phase file to obtain phase details for different Crema versions.

    Parameters
    ----------
    crema_version : str, optional
        Crema version identifier (e.g., '3_0', '3_1', '3_2'...).
    file_path : str, optional
        Path to the mission phase file (default: '').

    Returns
    -------
    dict
        Dictionary containing phase details (name, description, start time, end time) for each phase.

    Note:
    -----
    Superseedes IDL Read_Mission_Phase_file from Planning.pro
    """
    mission_phases = {}

    if crema_version:
        file_path = f"{CONF_PATH}/internal/geopipeline/output/Crema_{crema_version}/Mission_Phases.csv"
    elif not file_path:
        raise "Mission Phase file not specified."

    with open(file_path, "r") as file:
        lines = file.readlines()

        for line in lines[1:]:  # Skip the header line
            values = line.strip().split(',')

            phase = {
                "name": values[0],
                "desc": values[1],
                "t_start": values[2],
                "t_end": values[3]
            }

            mission_phases[values[0]] = phase

    return mission_phases


def get_mission_phase_times(crema_version, mission_phase):
    """
    Get start and end times for a specific mission phase and Crema version.

    Parameters
    ----------
    crema_version : str
        Crema version identifier (e.g., '3_0', '3_1', '3_2'...).
    mission_phase : str
        Name of the mission phase.

    Returns
    -------
    tuple
        Tuple containing start and end times (in UTC) for the specified mission phase and Crema version.
    """
    mission_phases = read_mission_phase_file(crema_version=crema_version)
    utc_start = mission_phases[mission_phase]["t_start"]
    utc_end = mission_phases[mission_phase]["t_end"]

    return utc_start, utc_end


