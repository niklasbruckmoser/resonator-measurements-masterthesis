import numpy as np
from PyLab.Measurement import *

def get_linspace(f_s, f_e, q_c, df_res):
    """
    Calculates the number of points to achieve a reasonable resolution
    :param f_s: start frequency
    :param f_e: end frequency
    :param q_c: coupling quality factor
    :param df_res: number of points in the fwhm, assuming q_l=q_c
    :return: the number of points
    """
    df = f_s/q_c
    f_res = df/df_res

    return np.linspace(f_s, f_e, int((f_e-f_s)/f_res))


def get_linspace_spectrum(f_s, f_e, q_c=1e5):
    """
    Get the linspace for the whole spectrum
    """
    return get_linspace(f_s, f_e, q_c, df_res=2)


def get_linspace_preprecise(f_c, q_c, df_res=5):
    """
    get the linspace for a preprecise fit to determine an estimate for the loaded quality factor
    """
    lr_spacing = 40  # left and right spacing, 25
    df = f_c/q_c
    f_s = f_c - lr_spacing*df
    f_e = f_c + lr_spacing*df
    return get_linspace(f_s, f_e, q_c, df_res)


def get_linspace_precise(f_c, q_l, df_res=40):
    """
    Get the linspace for a precise fit around the resonance frequency
    """
    lr_spacing = 6  # left and right spacing, 3.5
    df = f_c/q_l
    f_s = f_c - lr_spacing*df
    f_e = f_c + lr_spacing*df


    return get_linspace(f_s, f_e, q_l, df_res)


def get_params_spectrum():
    """
    :return: bandwidth, power, averages
    """
    return 1000, 0, 1

def get_params_preprecise(warm_attenuation):
    """
    :return: bandwidth, power, averages
    """
    if warm_attenuation == -10:
        return 100, -10, 1
    elif warm_attenuation == -60:
        return 50, 10, 5
    else:
        print("invalid warm attenuation!")
        return 100, 0, 1


def get_paramlist_precise(warm_attenuation):
    """
    :return: list of bandwidth, power, averages for 6 values
    """
    if warm_attenuation == -10:
        return [(1000, 10, 1),
                (1000, 5, 1),
                (1000, 0, 1),
                (1000, -5, 1),
                (1000, -10, 1),
                (1000, -15, 1),
                (1000, -20, 1),
                (1000, -25, 1),
                (100, -30, 1),
                (100, -35, 1)]
    elif warm_attenuation == -60:
        return [(50, 10, 5),
                (10, 5, 10),
                (10, 0, 10),
                (10, -5, 20),
                (10, -10, 20),
                (10, -15, 30),
                (10, -20, 30),
                (10, -25, 40),
                (10, -30, 40),
                (10, -35, 50),
                (10, -40, 50)]
    else:
        print("invalid warm attenuation!")
        return []
