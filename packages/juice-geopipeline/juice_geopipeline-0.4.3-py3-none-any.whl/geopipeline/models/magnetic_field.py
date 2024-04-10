"""
Module Description: Functions related to Jupiter's magnetic field analysis as provided by the PEP team.
"""

import JupiterMag as jm
import numpy as np

import spiceypy as spice

import matplotlib.pyplot as plt


def magnetic_field_vector(et_array):
    """
    Calculate the total magnetic field vector at a given array of times.

    Parameters
    ----------
    et_array : array-like
        Array of Ephemeris Times (ET).

    Returns
    -------
    np.ndarray
        Array containing the x, y, z components of the magnetic field in IAU_JUPITER coordinates (nT).
    """
    # positions in Jupiter radii and in IAU_JUPITER (1 Rj = 71492km)
    if isinstance(et_array, float):
        et_array = [et_array]

    juipos, lt = spice.spkpos('JUICE', et_array, 'IAU_JUPITER', 'NONE', 'JUPITER')
    jupiter_radii = spice.bodvrd('JUPITER', 'RADII', 3)[1]

    # use jrm33 internal magnetic field model in cartesian coordinates (x,y,z).
    # In put coordinates are in IAU_JUPITER in units of Jupiter radii (1 Rj = 71492 km)
    x = juipos[:,0] / jupiter_radii[0]
    y = juipos[:,1] / jupiter_radii[0]
    z = juipos[:,2] / jupiter_radii[0]

    # Internal magnetic field
    B_int = np.array(jm.Internal.Field(x, y, z))
    # External magnetic field
    B_ext = np.array(jm.Con2020.Field(x, y, z))

    B_total = B_int + B_ext

    # array with the x, y, z IAU_JUPITER components of the magnetic field in nT
    transposed_B = list(zip(*B_total))
    B_total_arrays = [np.array(t) for t in transposed_B]
    return np.array(B_total_arrays)


def l_shell(et_array, plot_magnetic_field_lines=False):
    """
    Calculate the L-shell distance of the magnetic equator from the planet center in jovian radii.

    Parameters
    ----------
    et_array : array-like
        Array of Ephemeris Times (ET).

    Returns
    -------
    np.ndarray
        Array containing the L-shell distances for each field line.
    """
    # T.R is the radial distance of any point on a traced field line.
    # The max distance of the field line in this field model coincides occurs at the magnetic equator crossing
    # This is termed as L-shell or M-shell, distance of the magnetic equator from the planet center in jovian radii
    # axis =1 is provided to get the L-shell from each of the four field lines
    if isinstance(et_array, float):
        et_array = [et_array]

    # positions in Jupiter radii and in IAU_JUPITER (1 Rj = 71492km)
    juipos, lt = spice.spkpos('JUICE', et_array, 'IAU_JUPITER', 'NONE', 'JUPITER')
    jupiter_radii = spice.bodvrd('JUPITER', 'RADII', 3)[1]

    # use jrm33 internal magnetic field model in cartesian coordinates (x,y,z).
    # Input coordinates are in IAU_JUPITER in units of Jupiter radii (1 Rj = 71492 km)
    x = np.array(juipos[:, 0]) / jupiter_radii[0]
    y = np.array(juipos[:, 1]) / jupiter_radii[0]
    z = np.array(juipos[:, 2]) / jupiter_radii[0]

    print(type(x))

    # Trace field lines using the input positions
    T = jm.TraceField(x, y, z, IntModel='jrm33', ExtModel='Con2020')

    if plot_magnetic_field_lines:
        # visualize the field lines
        ax = T.PlotRhoZ(label='JRM33 + Con2020', color='red')# R_cylndrical,Z plot (IAU_JUPITER)
        plt.show()

    # Calculate the L-shell
    lshell = np.nanmax(T.R, axis=1)

    return lshell


def pitch_angle(et_array, instrument='JUICE_PEP_JEI', direction=False):
    """
    Calculate the pitch angle of particles based on the given instrument direction.

    Parameters
    ----------
    et_array : array-like
        Array of Ephemeris Times (ET).
    instrument : str, optional
        Instrument name (default: 'JUICE_PEP_JEI').
    direction : array-like or False, optional
        Direction vector for the instrument in the instrument reference frame
        if not specified the instrument boresight is used (default: False).

    Returns
    -------
    list
        List of pitch angles for particles based on the instrument direction.
    """
    if isinstance(et_array, float):
        et_array = [et_array]

    B_total = magnetic_field_vector(et_array)

    shape, frame, bsight, n, bounds = spice.getfvn(instrument, 99, 99, 99)

    pitch_angle = []  # Generate array for storing pitch angle

    for b_total_temp, et_temp in zip(B_total, et_array):  # loop through both the magnetic field and et-time using zip
        mat = spice.pxform(frame, 'IAU_JUPITER', et_temp)  # JEI boresight is given in JUICE_PEP_JEI
        if direction:
            bsight = direction

        boresight_iau = spice.mxv(mat, bsight)  # rotation matrix is pform, use it to transofrom JUICE_PEP_JEI bs to IAU_JUPITER

        # angle between field vector &  boresight, in deg
        # notice this is the angle of the detector to the magnetic field.
        # The particle comes into the detector from the "anti-boresight" direction, so the particle pitch angle is 180-detector_pitch_angle
        detector_pitch_angle = spice.convrt(spice.vsep(boresight_iau, b_total_temp), 'RADIANS', 'DEGREES')
        pitch_angle.append(180.0 - detector_pitch_angle)

    return pitch_angle