import pyvisa
import numpy as np
import time
from datetime import datetime

class PNA():
    '''
    Small minimalist python driver for S21 measurements with the Keysight PNA
    NB 08/2021
    '''

    def __init__(self, address, sweep_mode='LIN', channel_index=1):

        self._address = address
        self._visainstrument = pyvisa.ResourceManager().open_resource(self._address, timeout=5000)
        self._ci = channel_index

        #default init values
        self.power = -20
        self.bandwidth = 100
        self.averages = 1
        self.sweep_mode = sweep_mode
        self.frequencies = np.linspace(4e9, 6e9, 1001)
        self.fixed_frequency = 5e9

    def query(self, cmd: str):
        """
        Query a SCPI command
        :param cmd: SCPI command
        :return: evaluation of the SCPI command
        """
        return self._visainstrument.query(cmd)

    def write(self, cmd: str):
        """
        Write a SCPI command
        :param cmd: SCPI command
        """
        # write a SCPI command
        self._visainstrument.write(cmd)

    def wait(self):
        """
        Sends an OPC query to block the pipeline until the operacion is complete
        :return: 1 as soon as the operation is complete
        """
        return self._visainstrument.query('*OPC?')


    def set_rf_on(self):
        """
        Turn the output on
        """
        self.write('OUTPut:STATe ON')
        self._output = True

    def set_rf_off(self):
        """
        Turn the output off
        """
        self.write('OUTPut:STATe OFF')
        self._output = False

    def set_frequencies(self, start: float, stop: float, nop: int):
        """
        Set the frequencies for the sweep
        :param start: start frequency in Hz
        :param stop: stop frequency in Hz
        :param nop: number of points
        """
        self.frequencies = np.linspace(start, stop, nop)
        self.write(f':SENSe{self._ci}:SWEep:POINts {len(self.frequencies)}')
        self.write(f':SENSe{self._ci}:FREQuency:STARt {self.frequencies[0]:.3f}')
        self.write(f':SENSe{self._ci}:FREQuency:STOP {self.frequencies[-1]:.3f}')

    def set_frequency_center(self, center: float, span: float, nop: int):
        """
        Set the frequencies for the sweep
        :param center: center frequency in Hz
        :param span: full frequency span in Hz
        :param nop: number of points
        """
        self.set_frequency(center-span/2, center+span/2, nop)

    def set_fixed_frequency(self, fixed_frequency: float):
        """
        Set the continuous wave frequency
        :param fixed_frequency: fixed frequency in Hz
        """
        self.fixed_frequency = fixed_frequency
        self.write(f':SENSe{self._ci}:FREQuency:CW {self.fixed_frequency:.3f}')

    def set_power(self, power: float):
        """
        Set the output power in dBm
        :param power: power in dBm
        """
        self.power = power
        self.write(f':SOURce{self._ci}:POWer {self.power}')

    def set_bandwidth(self, bandwidth: int):
        """
        Set the IF bandwith of the VNA
        :param bandwidth: bandwidth in Hz
        """
        self.bandwidth = bandwidth
        self.write(f'SENSe{self._ci}:BANDwidth:RESolution {self.bandwidth}')

    def set_sweep_mode(self, mode: str):
        """
        Set the sweep mode of the VNA
        :param mode: sweep mode, either LIN for sweeps or POINt for CW measurements
        """
        if mode.upper() in ["LIN", "POINT"]:
            self.sweep_mode = mode
            self.write(f"SENSe{self._ci}:SWEep:TYPE {self.sweep_mode}")
        else:
            ValueError("Sweep mode must be LIN (default) or POINt (fixed/cw frequency).")

    def set_averages(self, averages: int):
        """
        Set the amount of sweep averages
        :param averages: amount of averages, 1 means no averaging
        """
        if averages == 0 or averages == 1:
            self.averages = 1
            self.write(f'SENSe{self._ci}:AVERage:STATe OFF')
        else:
            self.averages = averages
            self.write(f'SENSe{self._ci}:AVERage:STATe ON')
            self.write(f'SENSe{self._ci}:AVERage:COUNt {self.averages}')

    def set_average_mode(self, mode: str):
        """
        Set the mode of averaging
        :param mode: Either POINt for averaging each point x times, or SWEep for sweeping x times
        """
        if mode.upper() in ["POINT", "SWEEP"]:
            self.write(f"SENSe{self._ci}:AVERage:MODE {mode}")
        else:
            ValueError('Average mode must be POINt (averaging each point x times) or SWEep (sweeping x times).')

    def measure(self):
        """
        Perform a measurement with the chosen settings. Make sure everything is set
        :return: dictionary containing the measured S parameter data
        """
        # doing the dirty timeout way to make sure measurement runs fine
        self.write("INIT:CONT OFF")
        old_timeout = self._visainstrument.timeout
        full_time = self.get_sweep_time()
        now = datetime.now()
        dt_string = now.strftime("%H:%M")
        print(f"current time: {dt_string} - sweep time: {int(np.floor(full_time/3600)):02d}:{int(np.floor((full_time%3600)/60)):02d}:{int(full_time%60):02d} h:m:s")
        self._visainstrument.timeout = full_time*1000 + 5000

        for i in range(self.averages):
            # Clear status, initiate measurement
            self.wait()
            self.write("*CLS;INIT:IMM;*OPC")
            # Check first bit in the event status register for OPC
            while not (int(self.query("*ESR?")) & 1):
                time.sleep(0.002)

        time.sleep(0.2)
        self.wait()
        self._visainstrument.timeout = old_timeout
        return {'S-parameter': self.get_data()}

    def get_data(self):
        """
        Get the measured complex data
        :return: complex-valued np array
        """
        # data = self.query(r'CALCulate:DATA? SDATa')
        data = self._visainstrument.query_ascii_values("CALCulate:DATA? SDATa")
        data_size = np.size(data)
        datareal = np.array(data[0:data_size:2])
        dataimag = np.array(data[1:data_size:2])
        return datareal + 1j * dataimag

    def get_sweep_time(self):
        """
        Get the sweep time in seconds
        :return: full sweep time in seconds
        """
        return float(self.query(f':SENSe{self._ci}:SWEep:TIME?'))*self.averages

    #####################################################################
    # VNA SCPI Getter methods

    def get_power(self):
        """
        Get the power
        :return: power in dBm
        """
        return float(self.query(f':SOURce{self._ci}:POWer?'))

    def get_frequencies(self):
        """
        Get the frequencies
        :return: frequencies as a np linspace
        """
        start = self.get_start_freqency()
        stop = self.get_stop_freqency()
        nop = self.get_nop()
        return np.linspace(start, stop, nop)

    def get_start_freqency(self):
        """
        Get the start sweep frequency
        :return: start frequency in Hz
        """
        return float(self.query(f':SENSe{self._ci}:FREQuency:STARt?'))
        # return self._start

    def get_stop_freqency(self):
        """
        Get the stop sweep frequency
        :return: stop frequency in Hz
        """
        return float(self.query(f':SENSe{self._ci}:FREQuency:STOP?'))

    def get_bandwidth(self):
        """
        Get the IF bandwidth
        :return: bandwidth in Hz
        """
        return float(self.query(f'SENSe{self._ci}:BANDwidth:RESolution?'))

    def get_nop(self):
        """
        Get the number of frequency sweep points
        :return: number of sweep points
        """
        return int(self.query(f':SENSe{self._ci}:SWEep:POINts?'))

    ##########################################################################################
    # VNA setup

    def create_measurement_and_trace(self, window_number=1, measurement_name="S21 measurement", measurement_type="S21",
                                     trace_number=1):
        """
        Creates a new measurement and assigns it to a trace. Not sure if measurements and traces are overwritten if the
        same name is chosen.
        :param window_number: number of the window, by default 1
        :param measurement_name: name of the measurement
        :param measurement_type: type of measurement, by default "S21"
        :param trace_number: number of the trace, by default 1
        :param trace_name: name of the trace
        """
        # create window if not present
        if not self.query(f"DISPlay:WINDow{window_number}:STATe?"):
            self.write(f"DISPlay:WINDow{window_number}:STATe ON")

        # try to delete measurement with that name
        self.write(f"CALCulate{self._ci}:PARameter:DELete:NAME '{measurement_name}'")
        self.query("*OPC?")
        # create a measurement
        self.write(f"CALCulate{self._ci}:PARameter:DEFine:EXTended '{measurement_name}', '{measurement_type}'")
        self.query("*OPC?")
        # link the measurement to the trace by first deleting a potential existing trace (necessary? idk, maybe try out)
        # self.write(f"DISPlay:WINDow{window_number}:TRACe{trace_number}:DELete")
        self.write(f"DISPlay:WINDow{window_number}:TRACe{trace_number}:FEED '{measurement_name}'")

    ##################################
    # Legacy stuff

    # def set_all_parameters(self):
    #     self.set_power(self.power)
    #     self.set_bandwidth(self.bw)
    #     if (self.sweep_mode == 'LIN'):
    #         self.set_frequencies(self.start_freq, self.stop_freq, self.nop)
    #         self.set_average(self.average_mode)
    #         self.set_averages(self.averages)
    #     elif (self.sweep_mode == 'CW'):
    #         #set fixed CW frequency
    #         self.set_fixed_frequency(self.fixed_cw_frequency)
    #         #set CW time
    #
    #         #set CW interval between measurements