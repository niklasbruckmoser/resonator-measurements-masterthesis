hbar = 1.0545718e-34
pi = 3.1415926536

def dBm_to_watts(dBm: float):
    return 10**(dBm/10)/1000

def mean_photon_number(w_res, Q_l, Q_c, P):
    return 2/(hbar*w_res**2)*50/50*Q_l**2/Q_c*P


