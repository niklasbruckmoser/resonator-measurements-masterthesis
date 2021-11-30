import numpy as np
from pathlib import Path
import pickle


"""
class for keeping measurement info and data at a single place
"""


class Measurement:

    def __init__(self, operator, chip, bandwidth, power, frequencies, averages=1, sub_folder="", comment="", measurement_type='S21'):
        """
        Measurement initialization

        :param operator: name of the operator
        :param chip: name of the chip
        :param bandwidth: bandwidth that will be used for the measurement
        :param power: power of the VNA
        :param frequencies: 1D array containing the probe frequencies
        :param averages: amount of averages that will be used
        :param measurement_type: scattering parameter that will be used for the measurement. 'S21' by default
        """
        self._operator = operator
        self._chip = chip

        self._sub_folder = (sub_folder + "/") if sub_folder != "" else ""

        self._bandwidth = bandwidth
        self._power = power

        self._frequencies = frequencies
        self._data = []

        self._averages = averages
        self._measurement_type = measurement_type
        self._comment = comment

    # getters and setters to make parameters somewhat "constant"

    def set_data(self, data):
        """
        Set the measured data of the VNA

        :param data: 1D array containing the measurement data
        """
        self._data = data

    def get_operator(self):
        """
        Get the operator of this measurement

        :return: the operator
        """
        return self._operator

    def get_chip(self):
        """
        Get the name of the chip used in this measurement

        :return: the chip name
        """
        return self._chip

    def get_bandwidth(self):
        """
        Get the bandwidth

        :return: the bandwidth in Hz
        """
        return self._bandwidth

    def get_power(self):
        """
        Get the power output level of the VNA

        :return: the power in dBm, not containing attenuators outside of the VNA
        """
        return self._power

    def get_averages(self):
        """
        Get the amount of averages used in the measurement

        :return: the amount of averages
        """
        return self._averages

    def get_measurement_type(self):
        """
        Get the scattering parameter, e.g. 'S21'

        :return: the measurement type
        """
        return self._measurement_type

    def get_frequencies(self):
        """
        Get a 1D array containing the probed frequencies

        :return: a list containing the frequencies
        """
        return self._frequencies

    def get_data(self):
        """
        Get the measurement data

        :return: a list containing the data
        """
        return self._data

    # Utility methods

    # base_path=r"C:\Users\di67piz\Documents\Measurements\Results"
    def save(self, base_path=r"D:\Measurements\Resonators"):
        """
        Save the measurement data as 1. a raw txt file containing the frequency-data pairs and 2. a pickle object

        :param base_path: base path, not containing the operator or chip name
        :return: the path to the result data, without suffix
        """

        if len(self._frequencies) != len(self._data):
            raise ValueError("frequency and data size do not match")

        f_start = self._frequencies[0]
        f_end = self._frequencies[-1]
        bw = self._bandwidth
        nop = len(self._frequencies)
        power = self._power
        avg = self._averages
        name = f"measurement_{f_start/1e9:.2f}-{f_end/1e9:.2f}GHz_nop{nop}_bw{bw}_{power}dBm" + (f"_{avg}avgs" if avg > 1 else "")

        # path = f"{base_path}\\{self._operator}\\{self._chip}\\{name}"
        path = f"{base_path}/{self._operator}/{self._chip}/{self._sub_folder}{name}"


        # do not overwrite measurement data, rather save as a higher version number
        i = 1
        while True:
            if not Path(path + ".pickle").exists():
                # print(f"Path {path}.pickle does not exist.")
                Path(f"{base_path}/{self._operator}/{self._chip}/{self._sub_folder}").mkdir(parents=True, exist_ok=True)
                break
            else:
                # print(f"Path {path}.pickle does already exist. Trying v{i+1}.")
                i += 1
                path = f"{base_path}/{self._operator}/{self._chip}/{self._sub_folder}{name}_v{i}"

        # save object with pickle
        with open(f"{path}.pickle", "wb") as handle:
            pickle.dump(self._data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # save tab separated data manually
        with open(f"{path}.txt", "w+") as handle:
            lines = []
            if self._comment != "":
                for comment in self._comment.splitlines():
                    lines.append(f"# {comment}\n")
            for j in range(len(self._frequencies)):
                lines.append(str(self._frequencies[j]) + "\t" + str(self._data[j]) + "\n")
            handle.writelines(lines)

        return path  # return path, without suffix
