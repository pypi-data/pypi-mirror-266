import argparse
import logging
import spiceypy as spice

from textwrap import dedent

from geopipeline.science_planning import jupiter_tour_flip_zaxis_windows
from geopipeline.geometry.finder import jovian_system_occultations
from geopipeline.geometry.support import jupiter_altitude_limit

from .setup import get_version_from_setup_cfg
VERSION = get_version_from_setup_cfg()

logging.basicConfig(level=logging.INFO, format='%(message)s')


def list_of_strings(arg):
    '''
    Define a custom argument type for a list of string.

    Parameters
    ----------
    arg

    Returns
    -------
    lstr_uppercase
        List of strings in uppercase.
    '''
    lstr = arg.split(',')
    lstr_uppercase = [item.upper() for item in lstr]
    return lstr_uppercase


def cli_jupiter_tour_flip_zaxis_windows():
    """
    Command Line Interface function for generating Jupiter tour flip +Z axis windows.

    Usage: python script_name.py crema_version [--meta_kernel META_KERNEL]
            [--mission_phase MISSION_PHASE] [--utc_start UTC_START] [--utc_end UTC_END]
            [--duration DURATION] [--mission_timeline_event_file MISSION_TIMELINE_EVENT_FILE]
            [--output OUTPUT]

    Parameters
    ----------
    No direct parameters; uses argparse to handle command line arguments.

    Returns
    -------
    None
    """
    parser = argparse.ArgumentParser(description=f"geopipeline-{VERSION} CLI - UC41 - Jupiter Tour Flip +Z Axis Windows")

    # Positional arguments
    parser.add_argument('crema_version', type=str, help='Crema version.')

    # Optional arguments (with default values)
    parser.add_argument('-m','--meta_kernel', type=str, help='SPICE meta-kernel path')
    parser.add_argument('-p','--mission_phase', type=str, default='Jupiter_Phase_all',
                        help='Mission Phase to determine start and end times. Default: Jupiter_Phase_all')
    parser.add_argument('-b','--utc_start', type=str, help='Start time in UTC format')
    parser.add_argument('-e','--utc_end', type=str, help='End time in UTC format')
    parser.add_argument('-d','--duration', type=int, default=3600, help='Segment duration in seconds (default: 3600)')
    parser.add_argument('-f','--mission_timeline_event_file', type=str,
                        help='Path to the mission timeline event file')
    parser.add_argument('-o','--output', type=str,
                        help='Output file path (default: mission_timeline_event_file_{crema_version}.csv in conf repo)')

    args = parser.parse_args()

    if args.mission_phase and args.crema_version and (args.utc_start or args.utc_end):
        print('MISSION_PHASE and CREMA_VERSION provided but using UTC_START or UTC_END')
        return

    jupiter_tour_flip_zaxis_windows(
            mission_phase=args.mission_phase,
            crema_version=args.crema_version,
            utc_start=args.utc_start,
            utc_end=args.utc_end,
            duration=args.duration,
            mission_timeline_event_file=args.mission_timeline_event_file,
            output=args.output,
            meta_kernel=args.meta_kernel
        )

    return


def cli_jovian_system_occultations():
    """
        Command Line Interface function for generating Jupiter tour flip +Z axis windows.

    Usage: python script_name.py crema_version [--meta_kernel META_KERNEL]
            [--mission_phase MISSION_PHASE] [--utc_start UTC_START] [--utc_end UTC_END]
            [--duration DURATION] [--mission_timeline_event_file MISSION_TIMELINE_EVENT_FILE]
            [--output OUTPUT]

    Parameters
    ----------
    No direct parameters; uses argparse to handle command line arguments.

    Returns
    -------
    None
    """
    header = dedent(
            f"""\
    geopipeline-{VERSION} CLI - Jovian System Occultations

    This API searches for occultations for the specified target by the Jovian System. The Jovian
    system is a construct that includes the planet Jupiter, its rings and its moons. The system itself
    can be specified as a parameter. The following bodies can be used for the occultations:

    - Jupiter: JUPITER. Even it not specified Jupiter is always included in the system but its
      occultations will not be displayed as results (they are used to discriminate occultations hidden
      by Jupiter itself).
    - Moons: The Inner Moons, Galilean Moons, and irregular moons (any Moon available in the SPICE kernels).
    - Rings: You can either specify the Rings as a System (RINGS) or as individual rings. The rings are:
        - Halo Ring: JUICE_JUP_HALO_RING
        - Main Ring: JUICE_JUP_MAIN_RING
        - Gossamer Ring: JUICE_JUP_THE_GOS_RING
        - Amalthea Ring: JUICE_JUP_AMA_RING
        - Thebe Ring Extension: JUICE_JUP_THE_RING_EXT
    
    """
      )

    #
    # Build the argument parser.
    #
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=header)

    # Optional arguments (with default values)
    parser.add_argument('-m','--meta_kernel', type=str, help='SPICE meta-kernel path')
    parser.add_argument('-b','--utc_start', type=str, help='Start time in UTC format')
    parser.add_argument('-e','--utc_end', type=str, help='End time in UTC format')
    parser.add_argument('-p','--step', type=int, default=600, help='Calculation step (default: 600)')
    parser.add_argument('-a','--altitude', type=float, default=0, help='Jupiter altitude wrt to the 1 bar altitude (default: 0)')
    parser.add_argument('-t','--target', type=str, default='EARTH',
                        help='Target of the occultations by the system (default: EARTH)')
    parser.add_argument('-s','--system', type=list_of_strings, default=['JUPITER', 'IO', 'EUROPA', 'GANYMEDE', 'CALLISTO', 'RINGS'],
                        help="List of the bodies that form the Jovian System specified with their SPICE names. The bodies must be "
                             "separated with comas and without whitespaces "
                             "(default: JUPITER,IO,EUROPA,GANYMEDE,CALLISTO,RINGS)")

    args = parser.parse_args()

    spice.furnsh(args.meta_kernel)
    jupiter_altitude_limit(altitude=args.altitude)

    jovian_system_occultations(utc_start=args.utc_start, utc_end=args.utc_end, interval='', target=args.target,
                               system=args.system, step=args.step, occtyp='ANY', abcorr='LT+S', verbose=True)

    return