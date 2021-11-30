from PyLab.VNA import VNA
from PyLab.Measurement import Measurement
import matplotlib.pyplot as plt
from PyLab.CircleFit import notch_port
import numpy as np
import pyvisa

rough_peaks=[4273710000.0, 4479300000.0, 4.539e9, 4702530000.0, 4912740000.0, 5126520000.0, 5339040000.0, 5552190000.0, 5763660000.0, 5977650000.0, 6188910000.0]
operator = "NB"  # will be used for the folder
chip = "W5-32"  # will be used for the folder
# plot_save = "-10"  # -70 + power

attenuation = -66


nop = 501
span = 2e6

bandwidth = 100  # in Hz, 1000 by default
power = -10  # output power level of the VNA (between +? and -90 dBm)
averages = 1  # number of averages, by default 1 (i.e. no averaging)

# print(pyvisa.ResourceManager().list_resources())
# vna = VNA(address='TCPIP0::ZVA24-26-100428::inst0::INSTR')  # initiate the connection to the VNA (R&S ZVA24)
# vna = VNA(address='TCPIP0::10.1.1.15::inst0::INSTR')
vna = VNA(address='TCPIP0::10.1.1.32::inst0::INSTR')
print(vna.query_command("*IDN?"))

chip = chip + "/peakfinding"
#%% md

### Measure the whole spectrum

fine_peaks = []

for peak in rough_peaks:
    frequencies = np.linspace(peak-span/2, peak+span/2, nop)
    meas = Measurement(operator, chip, bandwidth, power, frequencies, averages)
    vna.set_measurement(meas)
    try:
        vna.rf_on()
        print("rf on")
        path = vna.measure()
        print("measured")
    finally:
        vna.rf_off()
        print("rf off")
    
    freq = meas.get_frequencies()
    s21 = meas.get_data()
    fit = notch_port(freq, s21)
    fit.autofit()
    f = fit.fitresults["fr"]
    fine_peaks.append(int(f))
    fit.plotall(path + ".pdf")
    # fit.plotall()

print(fine_peaks)