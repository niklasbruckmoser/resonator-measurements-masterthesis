from Results.NB.PyLab.VNA import VNA
from Results.NB.PyLab.Measurement import Measurement
import Results.NB.PyLab.PeakFinder as PeakFinder
import matplotlib.pyplot as plt
import numpy as np
import pyvisa

operator = "NB"  # will be used for the folder
chip = "test"  # will be used for the folder
# plot_save = "-10"  # -70 + power

attenuation = -70

f_start = 4e9
f_end = 5.3e9

num_peaks = 12

nop = 10001

bandwidth = 1000  # in Hz, 1000 by default
power = -20  # output power level of the VNA (between +? and -90 dBm)
averages = 1  # number of averages, by default 1 (i.e. no averaging)

find_frequencies = False

# print(pyvisa.ResourceManager().list_resources())
# vna = VNA(address='TCPIP0::ZVA24-26-100428::inst0::INSTR')  # initiate the connection to the VNA (R&S ZVA24)
# vna = VNA(address='TCPIP0::10.1.1.15::inst0::INSTR')
vna = VNA(name='PNA', address='TCPIP0::10.1.1.32::inst0::INSTR')  # Keysight VNA
print(vna.query_command("*IDN?"))
#%% md

### Measure the whole spectrum

frequencies = np.linspace(f_start, f_end, nop)
spectrum_measurement = Measurement(operator, chip, bandwidth, power, frequencies, averages)

# vna.create_measurement_and_trace(1, "test_measurement", "S21", 1, "S21_trace")
vna.wait()

vna.set_measurement(spectrum_measurement)
print(f"Sweep time: {vna.get_measurement_time()}")
try:
    vna.rf_on()
    print("rf on")
    vna.measure(save=False)
    print("measured")
finally:
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