from PyLab.VNA import VNA
from PyLab.Measurement import Measurement
import PyLab.PeakFinder as PeakFinder
import matplotlib.pyplot as plt
import numpy as np
import pyvisa

operator = "JS"  # will be used for the folder
chip = "8 port S37"  # will be used for the folder
# plot_save = "-10"  # -70 + power

attenuation = 0

f_start = 1e8
f_end = 40e9

num_peaks = 11

nop = 10001

bandwidth = 20  # in Hz, 1000 by default
power = 10  # output power level of the VNA (between +? and -90 dBm)
averages = 1  # number of averages, by default 1 (i.e. no averaging)

find_frequencies = False

# print(pyvisa.ResourceManager().list_resources())
# vna = VNA(address='TCPIP0::ZVA24-26-100428::inst0::INSTR')  # initiate the connection to the VNA (R&S ZVA24)
# vna = VNA(address='TCPIP0::10.1.1.32::inst0::INSTR')
vna = VNA(name='PNA', address='TCPIP0::10.1.1.32::inst0::INSTR')  # Keysight VNA
# vna = VNA(name='PNA', address='TCPIP0::10.1.1.25::inst0::INSTR')  # R&S VNA
print(vna.query_command("*IDN?"))
#%% md

### Measure the whole spectrum

frequencies = np.linspace(f_start, f_end, nop)
spectrum_measurement = Measurement(operator, chip, bandwidth, power, frequencies, averages)
# vna.run_command("CALC:PAR:SEL 'CH1_S21_1'")
vna.set_measurement(spectrum_measurement)
try:
    vna.rf_on()
    print("rf on")
    vna.measure()
    print("measured")
finally:
    vna.wait()
    vna.rf_off()
    print("rf off")

freq = spectrum_measurement.get_frequencies()
s21 = spectrum_measurement.get_data()

if find_frequencies:
    peaks = PeakFinder.find_peaks(freq, s21, num_peaks)
    print(peaks)

plt.figure(0)
plt.plot(freq, np.abs(s21))
plt.show()