import os
import configparser

import spiceypy as spice
from planetary_coverage import MetaKernel, ESA_MK
from dotenv import load_dotenv
from pathlib import Path
from shutil import copy

load_dotenv()

def get_version_from_setup_cfg():
    """
    Extract the version from the setup.cfg file.

    Returns
    -------
    str or None
        The version string if found in the 'metadata' section of the setup.cfg file,
        otherwise returns None.
    """
    config = configparser.ConfigParser()

    config.read(f'{os.path.dirname(os.path.abspath(__file__))}/../../setup.cfg')
    # Check if the 'metadata' section exists and contains 'version'
    if 'metadata' in config and 'version' in config['metadata']:
        return config['metadata']['version']
    else:
        return None  # Return None if version is not found


def geopipeline_path():
    """
    Get the path for the geopipeline.

    Returns
    -------
    str or None
        The path to the GeoPipeline environment variable or None if not found.
    """
    return os.getenv('GEOPIPELINE')


def conf_path():
    """
    Get the path for the configuration repository.

    Returns
    -------
    str or None
        The path to the configuration repository environment variable or None if not found.
    """
    return os.getenv('CONF_REPO')


def furnsh(kernel):
    """Load a given kernel to the kernel pool.

    Parameters
    ----------
    kernel : str
        Path of the kernel to load.
    """
    spice.furnsh(kernel)


def get_kernels_dir(env=None):
    """Get the directory for the JUICE SPICE Kernels.

    Parameters
    ----------
    env : str, optional
        Path of the environmental file to load.

    Returns
    -------
    kernels_dir : str
        JUICE SPICE Kernels directory.
    """
    load_dotenv(env)
    kernels_dir = os.getenv('KERNELS_JUICE')
    return kernels_dir


def local_kernels(kernels_dir=None, mk='plan'):
    """Download the kernels from a given MK locally.

    The function also creates a copy of the MK with the
    ``PATH_VALUE`` replaced by the ``kernels_dir``

    Arguments
    ---------
    kernels_dir : str, optional
        JUICE SPICE Kernels directory. Loaded from the
        directory specified by env file if not specified.
    mk : str, optional
        ``MK_IDENTIFIER`` for the kernels within meta-kernel
        to download. Set to the latest version of ``PLAN`` kernels
        if not specified.

    Returns
    -------
    mk_local : str
        Path to the created local meta-kernel.

    """
    if not kernels_dir:
        kernels_dir = get_kernels_dir()

    metakernel = MetaKernel(ESA_MK['JUICE', mk], kernels=kernels_dir, download=True)
    mk_id = metakernel.data['MK_IDENTIFIER']
    try:
        os.mkdir(f"{kernels_dir}/mk")
    except:
        pass

    mk_local = Path(f"{kernels_dir}/mk/{mk_id}_local.tm")

    # we need the context manager in order to keep the file existing.
    with metakernel as f:
        copy(f, mk_local)
    mk_local = str(mk_local)

    return mk_local