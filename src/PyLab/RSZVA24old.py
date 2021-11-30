import pyvisa
import numpy
import time


class RSVNA():
    '''
    This is the python driver for Rohde&Schwarz vector network analyzers (written specifically for ZVA26 connected via TCP/IP address)
    '''

    def __init__(self, address, sweep_mode = 'LIN', channel_index=1,start_freq = 4e9, stop_freq =6e9, fixed_cw_frequency = 6e9):
        '''
        Initializes
        Input:
            name (string)	: name of the instrument
            address (string) : TCP/IP address like 'TCPIP0::ZVA24-26-100428::inst0::INSTR'
        '''


        self._address = address
        print(f"opening resource with address {self._address}")
        self._visainstrument = pyvisa.ResourceManager().open_resource(self._address, timeout=5000)
        self._ci = channel_index


        #measurement parameters default values
        self.power = -40
        self.bw = 10
        self.nop = 1000
        self.start_freq = start_freq
        self.stop_freq = stop_freq
        self.span = 4e9
        self.center_freq = 6e9
        self.average_mode = False
        self.averages = 1
        self.sweep_mode = sweep_mode
        self.frequencies = numpy.linspace(self.start_freq, self.stop_freq, self.nop)
        self._zerospan= False
        self.fixed_cw_frequency = fixed_cw_frequency

        # self.stop_frequencies =

        self._output = False  # TODO make sure that output is false
    def set_sweep_mode(self):
        if (self.sweep_mode == 'CW'):
            self.write('SENS%i:SWE:TYPE %s' % (self._ci, "POINt"))
        elif (self.sweep_mode == 'LIN'):
            self.write('SENS%i:SWE:TYPE %s' % (self._ci, "LIN"))

        return print("setting sweep mode to %s"%self.sweep_mode)
    def get_all(self):
        params = {}
        if self.sweep_mode == 'CW' and self.span == 0.0:
            params['power'] = self.power
            params['freq'] = self.start_freq
        elif self.sweep_mode == 'LIN':
            params['nop'] = self.nop
            params['power'] = self.power
            params['start freq'] = self.start_freq
            params['stop freq'] = self.stop_freq
            params['span'] = self.span
            params['bw'] = self.bw
            if self.averages != 1:
                params['averages'] = self.averages
                params['average mode'] = self.average_mode
        params['sweep mode'] = self.sweep_mode
        return params

    def query(self, cmd):
        # Just ask it .ask doesn't support tcp\ip
        return self._visainstrument.query(cmd)

    def write(self, cmd):
        # I want just write it
        return self._visainstrument.write(cmd)

    def wait(self):
        return self._visainstrument.query('*OPC?')

    def get_data(self):
        '''
        This function gives the data only when the measurement already was performed
        :return:
        '''
        # data = self._visainstrument.query(r'CALC:DATA? SDAT')
        data = self._visainstrument.query_ascii_values("CALC:DATA? SDAT")
        data_size = numpy.size(data)
        datareal = numpy.array(data[0:data_size:2])
        dataimag = numpy.array(data[1:data_size:2])
        return datareal + 1j * dataimag

    def set_frequencies(self, start, stop, nop):
        '''
        Set frequencies
        Input:
            start (float) : frequency in Hz
            stop (float) : frequency in Hz
            start (int) : number of points
        Output:
            None
        '''
        self.set_nop(nop)
        self.set_startfreq(start)
        self.set_stopfreq(stop)
        self.start_freq = start
        self.stop_freq = stop
        self.span = stop-start
        self.center_freq = (start+stop)/2
        self.frequencies = numpy.linspace(start, stop, nop)
        return self.frequencies
    def set_fixed_frequency(self, val):
        #val is the fixed frequency now
        self.write(':SENS%i:FREQ:FIX|CW %.3f' % (self._ci, val))
        return

    def set_nop(self, nop):
        '''
        Set Start frequency
        Input:
            span (float) : Frequency in Hz
        Output:
            None
        '''
        self.write(':SENS%i:SWE:POIN %i' %(self._ci, nop))
        self.nop = nop
        # return nop

    def set_startfreq(self, val):
        '''
        Set Start frequency
        Input:
            span (float) : Frequency in Hz
        Output:
            None
        '''
        self.start_freq = val
        self.write(':SENS%i:FREQ:STAR %f' % (self._ci, val))

    def set_stopfreq(self, val):
        '''
        Set STop frequency
        Input:
            val (float) : Stop Frequency in Hz
        Output:
            None
        '''
        self.stop_freq = val
        self.write(':SENS%i:FREQ:STOP %f' % (self._ci, val))
    def set_power(self, power):
        '''
        Set power
        Input:
            power (float) : power in dBm
        Output:
            None
        '''
        self.write(':SOURce%i:POWer %f' % (self._ci, power))
        self.power = power

    def set_rf_on(self):
        self.write('OUTPut:STATe ON')
        self._output = True

    def set_rf_off(self):
        self.write('OUTPut:STATe OFF')
        self._output = False


    #
    # def set_auto_loss_delay(self, input_port):
    #     self.measure()
    #     self.write('SENSe%i:CORRection:LOSS%i:AUTO ONCE' % (self._ci, input_port))

    def set_average(self, status):
        '''
        Set averaging status
        Input:
            status (bool)
        Output:
            None
        '''
        if status:
            self.average_mode = True
            self.write('SENS%i:AVER:STAT %s' % (self._ci, "ON"))
        else:
            self.average_mode = False
            self.write('SENS%i:AVER:STAT %s' % (self._ci, "OFF"))

    def set_averages(self, av):
        '''
        Set number of averages
        Input:
            av (int) : Number of averages
        Output:
            None
        '''
        # if self._zerospan:
        #     self._visainstrument.write('SWE:POIN %.1f' % (self._ci, av))
        # else:
        self.write('SENS%i:AVER:COUN %i' % (self._ci, av))
        self.averages = av



    def set_all_parameters(self):
        self.set_power(self.power)
        self.set_bandwidth(self.bw)
        if (self.sweep_mode == 'LIN'):
            self.set_frequencies(self.start_freq, self.stop_freq, self.nop)
            self.set_average(self.average_mode)
            self.set_averages(self.averages)
        elif (self.sweep_mode == 'CW'):
            #set fixed CW frequency
            self.set_fixed_frequency(self.fixed_cw_frequency)
            #set CW time

            #set CW interval between measurements

    def measure(self):

        self.set_all_parameters()

        old_timeout = self._visainstrument.timeout
        sweep_time = float(self.query('SENSe1:SWEep:TIME?'))
        # print(f"sweep time for 1 avg: {int(sweep_time)}s")
        self._visainstrument.timeout = sweep_time * 1000 + 5000

        for i in range(self.averages):
            # Clear status, initiate measurement
            self.write("*CLS;INIT:IMM;*OPC")
            # self.write(":DISPlay:WINDow1:TRACe1:Y:AUTO")
            # Check first bit im ESR (operation complete)
            while not (int(self._visainstrument.query("*ESR?")) & 1):
                time.sleep(0.002)
        # for ch in [1,2,3,4]:
        #     self.write('TRIGger%i:SEQuence:SOURce IMMediate' % (ch,))
        #     self.write('INITiate%i:IMMediate' % (ch,))

        # print(float(sweep_time / 1e3 * self.nop))
        time.sleep(.2)
        self.wait()
        # print(self.query('*OPC?'))
        self._visainstrument.timeout = old_timeout
        return {'S-parameter': self.get_data()}

    def get_sweep_time(self):
        """
        Get the time needed for one sweep

        Returns:
            out: float
                time in ms
        """
        return float(self.query(':SENS%i:SWE:TIME?' % (self._ci))) * 1e3

    def pre_sweep(self):
        # self.init()
        self.set_trigger_source("OFF")
        self.write("*ESE 1")
        self.set_average_mode("POIN")

    def post_sweep(self):
        self.set_trigger_source("ON")

    def set_trigger_source(self, source):
        '''
        Set Trigger Mode
        Input:
            source (string) : ON | OFF
        Output:
            None
        '''
        if source.upper() in ["ON", "OFF"]:
            self.write('INIT:CONT %s' % source.upper())
        else:
            raise ValueError('set_trigger_source(): must be ON | OFF ')

    def set_average_mode(self, mode):
        '''
        Set averaging mode
        Input:
            mode (string) AUTO | FLATten | REDuse | MOVing
        '''
        if mode.upper() in ["AUTO", "FLAT", "RED", "MOV", "FLATTEN", "REDUCE", "MOVING"]:
            self.write("SENS:AVER:MODE " + mode)
        else:
            ValueError('set_average_mode(mode): mode must be AUTO | FLATten | REDuse | MOVing')




    def set_bandwidth(self, band):
        self.bw = band
        self.write('SENS%i:BWID:RES %i' % (self._ci, band))
        return self.bw

    #####################################################################
    # in case you want to see what is going on now in the VNA
    def __get_power(self):
        return float(self.query(':SOURce%i:POWer?' % (self._ci)))

    def __get_span(self):
        '''
        Get Span

        Input:
            None
        Output:
            span (float) : Span in Hz
        '''
        return float(self._visainstrument.query('SENS%i:FREQ:SPAN?' % (self._ci)))
    def __get_freqpoints(self):
        start = self.__get_startfreq()
        stop = self.__get_stopfreq()
        nop = self.__get_nop()
        return numpy.linspace(start, stop, nop)
    def __get_startfreq(self):
        '''
        Get Start frequency

        Input:
            None
        Output:
            span (float) : Start Frequency in Hz
        '''
        return float(self._visainstrument.query(':SENS%i:FREQ:STAR?' % (self._ci)))
        # return self._start

    def __get_centerfreq(self):
        '''
        Get the center frequency
        Input:
            None
        Output:
            cf (float) :Center Frequency in Hz
        '''
        return float(self._visainstrument.query(':SENS%i:FREQ:CENT?' % (self._ci)))
    def __get_stopfreq(self):
        '''
        Get Stop frequency

        Input:
            None
        Output:
            val (float) : Start Frequency in Hz
        '''
        return float(self._visainstrument.query(':SENS%i:FREQ:STOP?' % (self._ci)))

    def __get_bandwidth(self):
        return float(self.query('SENS%i:BWID:RES?'%self._ci))

    def __get_nop(self):
        return int(self._visainstrument.query(':SENSe%i:SWEep:POINts?' % self._ci))

    def __get_all(self):
        params = {}
        if self.__get_sweep_mode() == 'CW\n' and self.get_span() == 0.0:
            params['power'] = self.__get_power()
            params['freq'] = self.__get_startfreq()
        elif self.__get_sweep_mode() == 'LIN\n':
            params['nop'] = self.__get_nop()
            params['power'] = self.__get_power()
            params['start freq'] = self.__get_startfreq()
            params['stop freq'] = self.__get_stopfreq()
            params['span'] = self.__get_span()
            params['bw'] = self.__get_bandwidth()
            if self.__get_average():
                params['averages'] = self.__get_averages()
                params['average mode'] = self.__get_average_mode()
        params['sweep mode'] = self.__get_sweep_mode()
        return params

    ##########################################################################################
    def create_trace(self, channel, name, meas_parameter):
        '''
    Like in manual control, traces can be assigned to a channel and
    displayed in diagram areas (see section Traces, Channels and
    Diagram Areas in Chapter 3).
    There are two main differences between manual and remote control:
    A trace can be created without being displayed on the screen.
    A channel must not necessarily contain a trace.
    Channel and trace configurations are independent of each other.
    Create new trace and new channel (if channel <Ch> does not exist yet)
    CALCulate<Ch>:PARameter:SDEFine '<Trace Name>','< Meas Parameter>
        '''
        return self._visainstrument.write("CALCulate{}:PARameter:SDEFine '{}','{}'".format(
            channel, name, meas_parameter))