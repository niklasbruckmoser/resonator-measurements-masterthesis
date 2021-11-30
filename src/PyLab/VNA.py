from PyLab.Measurement import *
# from Results.NB.PyLab.PNA import PNA
from PyLab.RSZVA24old import RSVNA as PNA

class VNA:
    '''
    Frontend object for interacting with the VNA (i.e. SCPI command free) in the Measurement framework.
    '''

    def __init__(self, name='ZVA24', address='TCPIP0::ZVA24-100169::inst0::INSTR'):
        """
        Initialize an object of the VNA class
        :param name: name of the VNA
        :param address: TCP/IP address of the instrument (can be found via NI MAX -> VISA resource name)
        """
        self._measurement = None
        self.pna = PNA(address)
        # self.pna.pre_sweep()

    def set_measurement(self, measurement: Measurement):
        """
        Sets the Measurement object for the VNA. The parameters will be directly set up in the VNA
        :param measurement: a Measurement object containing all the information for a measurement
        """
        self._measurement = measurement

        self.pna.set_power(self._measurement.get_power())
        self.pna.set_bandwidth(self._measurement.get_bandwidth())
        frequencies = self._measurement.get_frequencies()
        self.pna.set_frequencies(frequencies[0], frequencies[-1], len(frequencies))
        self.pna.set_averages(self._measurement.get_averages())

    def measure(self, save=True):
        """
        Start a VNA measurement with the parameters of the Measurement object
        :param save: if false, the data won't be saved
        :return: the path of the saved measurement data, without suffix - or None, if the data wasn't saved
        """
        if self._measurement is None:
            raise TypeError("Measurement has not been set yet!")
        self.pna.measure()
        self._measurement.set_data(self.pna.get_data())
        if save:
            return self._measurement.save()
        else:
            return None

    def get_measurement_time(self):
        return self.pna.get_sweep_time()

    def create_measurement_and_trace(self, window_number=1, measurement_name="S21 measurement", measurement_type="S21",
                                     trace_number=1):
        self.pna.create_measurement_and_trace(window_number, measurement_name, measurement_type, trace_number)

    def rf_on(self):
        self.pna.set_rf_on()

    def rf_off(self):
        self.pna.set_rf_off()

    def wait(self):
        self.pna.wait()

    def run_command(self, command):
        self.pna.write(command)

    def query_command(self, command):
        return self.pna.query(command)
