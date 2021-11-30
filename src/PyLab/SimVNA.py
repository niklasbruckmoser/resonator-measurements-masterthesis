from PyLab.Measurement import *
import numpy as np
import random
import random

class SimVNA:

    def __init__(self, seed=12345):
        """
        Initialize an object of the VNA class
        """
        self._measurement = None
        self._seed = seed

        self._lorentz_params = []
        random.seed(seed)
        for i in range(10):
            q_c = random.randint(150_000, 170_000)
            # q_i0 = random.randint(100_000, 140_000)
            q_i0 = 100_000
            # d_i = random.randint(20_000, 50_000)
            d_i = 50_000
            phi = 0 + random.random()*0.2 #0.3
            f_r = 4.1e9+0.2e9*i + random.randint(-10_000_000, 10_000_000)

            self._lorentz_params.append((q_c, q_i0, d_i, phi, f_r))


    def set_measurement(self, measurement: Measurement):
        """
        Sets the Measurement object for the VNA. The parameters will be used for the measurement
        :param measurement: a Measurement object containing all the information for a measurement
        """
        self._measurement = measurement

    def measure(self, save=True):
        """
        Start a VNA measurement with the parameters of the Measurement object
        :param save: if false, the data won't be saved
        :return: the path of the saved measurement data, without suffix - or None, if the data wasn't saved
        """
        if self._measurement is None:
            raise TypeError("Measurement has not been set yet!")

        data = []

        for f in self._measurement.get_frequencies():
            data.append(self._signal(f))

        self._measurement.set_data(data)
        print(len(self._measurement.get_data()))

        if save:
            return self._measurement.save()
        else:
            return None

    def _signal(self, f):
        sig = 1
        f_real = f - self._measurement.get_bandwidth()/2 + random.random()*self._measurement.get_bandwidth()
        for q_c, q_i0, d_i, phi, f_r in self._lorentz_params:

            q_i = q_i0 + d_i/(1+np.exp(-((self._measurement.get_power()+50)/70*8-4)))
            q_l = (1/q_i+1/np.real(q_c*np.exp(-1j*phi)))**-1

            sig -= _lorentz(q_l, q_c, phi, f_r, f_real)

        # complex signal + noise (maybe step up noise game in the future)
        noise = (random.random()-0.5)*0.01*(20-self._measurement.get_power())/10
        # noise = random.random()*0.0
        return sig + noise


def _lorentz(q_l, q_c, phi, f_r, f):
    # return a*np.exp(alpha*1j)*np.exp(-2*np.pi*1j*f*tau)*(q_l/abs(q_c)*np.exp(phi*1j)/(1+2j*q_l*(f/f_r-1)))
    return q_l/abs(q_c)*np.exp(1j*phi)/(1 + (2j*q_l*(f/f_r-1)))


if __name__ == "__main__":

    # freqs = np.linspace(4e9, 4.2e9, 100000)
    #
    # a = 1
    # alpha = 0.2
    # tau = 0.4
    # q_l = 1e5
    # q_c = 1.2e5
    # phi = 0.5
    # f_r = 4.1e9
    #
    # data = []
    #
    # for f in freqs:
    #     data.append((random.random()-0.5)*0.03+abs(a*np.exp(alpha*1j)*np.exp(-2*np.pi*1j*f*tau)*(1-_lorentz(a, q_l, q_c, phi, f_r, f))))

    vna = SimVNA(123)

    q_l = 1e5

    import PyLab.ResonatorTools as ResTools

    meas = Measurement("NB", "W5-2", 1000, 0, ResTools.get_linspace_spectrum(4e9, 6e9, q_l))

    vna.set_measurement(meas)
    vna.measure()

    import matplotlib.pyplot as plt

    plt.figure(0)
    plt.plot(meas.get_frequencies(), meas.get_data())
    plt.show()

