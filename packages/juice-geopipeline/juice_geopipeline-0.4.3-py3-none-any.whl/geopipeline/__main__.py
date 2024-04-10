"""**JUICE SOC geopipeline**.
"""
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from textwrap import dedent
from dotenv import dotenv_values

import json
from .setup import *

def main():

    version = get_version_from_setup_cfg()
    load_dotenv()

    header = dedent(
            f"""\
    geopipeline-{version}, JUICE Science Operations Center Geometric Event Calculator (geopipeline) 
    is a software package that provides geometrical computations for the JUICE mission.
        """
        )

    # Build the argument parser.
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter, description=header
    )
    parser.add_argument(
        "-m",
        "--metakernel",
        nargs='?',
        const="plan",
        action="store",
        type=str,
        help="Obtain the JUICE Kernels from a specific release "
             "locally including an updated copy of the meta-kernel (MK). "
             "The Default value is to obtain the latest PLAN MK. "
             "E.g. 'juice_plan_v421_20230124_001'",
    )

    parser.add_argument(
        "-e",
        "--environment",
        action="store_true",
        help="Display the environmental variables as obtained"
        "from the .env file in use.",
    )

    config = dotenv_values()
    if not config:
        print("WARNING: No environmental variables file found at ~/.env")
    # Store the arguments in the args object.
    args = parser.parse_args()

    if args.environment:
        if config:
            print(json.dumps(config, indent=4))

    if args.metakernel:
        KERNELS_DIR = get_kernels_dir()
        mk = local_kernels(KERNELS_DIR, args.metakernel)
        print(f'Meta-kernel available locally: {mk}')

    return None


if __name__ == "__main__":
    main()