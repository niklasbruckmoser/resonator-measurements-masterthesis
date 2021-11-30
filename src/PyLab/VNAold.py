import sys

sys.path.insert(0, "/home/measure/from windows PC/Measurements")
from PyLab.Measurement import *
import PyLab.RSZVA24old as RSZVA24


class VNA:

    def __init__(self, name='ZVA24', address='TCPIP0::ZVA24-100169::inst0::INSTR'):
        """
        Initialize an object of the VNA class
        :param name: name of the VNA
        :param address: TCP/IP address of the instrument (can be found via NI MAX -> VISA resource name)
        """
        self._measurement = None
        self.pna = RSZVA24.RSVNA(name, address)
        self.pna.pre_sweep()

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

        # set VNA parameters

        self.pna.set_power(self._measurement.get_power())
        self.pna.set_bandwidth(self._measurement.get_bandwidth())
        frequencies = self._measurement.get_frequencies()
        self.pna.set_frequencies(frequencies[0], frequencies[-1], len(frequencies))
        self.pna.set_average(True if self._measurement.get_averages() > 1 else False)
        self.pna.set_averages(self._measurement.get_averages())

        # TODO WATCH OUT
        # self.pna.write("SENS1:BWID 10")
        # self.pna.query("*OPC?")
        # print(self.pna.query("SENS1:BWID?"))

        # turn on VNA
        # TODO

        # start measuring and save data
        self.pna.measure()
        # self.pna.wait()  # maybe not necessary

        # turn off VNA -> maybe also manage turning on and off of VNA in the measurement script, if this more stable
        # than constantly turning on and off
        # TODO

        self._measurement.set_data(self.pna.get_data())
        if save:
            return self._measurement.save()
        else:
            return None

    def rf_on(self):
        self.pna.set_rf_on()

    def rf_off(self):
        self.pna.set_rf_off()

    def run_command(self, command):
        self.pna.write(command)

    def query_command(self, command):
        return self.pna.query(command)
