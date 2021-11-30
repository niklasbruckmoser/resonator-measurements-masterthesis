from PyLab.VNA import VNA
from PyLab.Measurement import Measurement
import matplotlib.pyplot as plt
from PyLab.CircleFit import notch_port
import numpy as np
import pyvisa
from datetime import datetime, timedelta

fine_peaks=[4273681600, 4478587244, 4539002588, 4702513076, 4912747880, 5126582026, 5339187224, 5552221202, 5763688478, 5977714474, 6189044588]
res_of_interest = [10]
# res_of_interest = [9]

operator = "NB"  # will be used for the folder
chip = "W5-32"  # will be used for the folder
subfolder = "run 11-02-2021"
# subfolder = "detailed resonance 9 11 nop"
attenuation = -72  # complete attenuation in input line (without VNA power)

nop = 301  # number of points, by default 501
span = 3e5  # span with f0 in center, by default 3e5

pow_bw_avg = [(-70, 100, 1), (-80, 100, 1), (-90, 100, 1), (-100, 10, 1), (-110, 10, 1), (-120, 5, 1), (-130, 1, 1), (-140, 1, 3)]
pow_bw_avg = [(-70, 100, 1), (-80, 100, 1), (-90, 100, 1), (-100, 10, 1), (-110, 10, 1), (-120, 10, 1), (-130, 5, 1), (-140, 1, 1), (-150, 1, 5), (-160, 1, 10)]  # low power sweeps
# pow_bw_avg = [(-70, 100, 1), (-80, 100, 1), (-90, 100, 1), (-100, 10, 1), (-110, 10, 1), (-120, 10, 1), (-130, 5, 3), (-140, 1, 5), (-150, 1, 10), (-160, 1, 20)]  # low power sweeps
# pow_bw_avg = [(-70, 100, 1), (-75, 100, 1), (-80, 100, 1), (-85, 100, 1), (-90, 100, 1), (-95, 100, 1), (-100, 10, 1),
#               (-105, 10, 1), (-110, 10, 1), (-115, 10, 1), (-120, 10, 1), (-125, 10, 1), (-130, 5, 3), (-135, 5, 5),
#               (-140, 1, 5), (-145, 1, 8), (-150, 1, 10), (-155, 1, 15), (-160, 1, 20)]  # detailed sweep
pow_bw_avg = [(-70, 100, 1), (-75, 100, 1), (-80, 100, 1), (-85, 100, 1), (-90, 100, 1), (-95, 100, 1), (-100, 10, 1),
              (-105, 10, 1), (-110, 10, 1), (-115, 10, 1), (-120, 10, 1), (-125, 10, 1), (-130, 1, 1), (-135, 1, 5),
              (-140, 1, 10), (-145, 1, 20), (-150, 1, 40)]  # detailed sweep
# pow_bw_avg = [(-70, 100, 1)]
# pow_bw_avg = [(-70, 100, 1), (-80, 100, 1), (-90, 100, 1)]
# pow_bw_avg = [(-150, 1, 50)]
###################
#
# CORE
#
###################


# vna = VNA(address='TCPIP0::10.1.1.15::inst0::INSTR')  # old RS VNA
vna = VNA(address='TCPIP0::10.1.1.32::inst0::INSTR')  # new keithley VNA
print(vna.query_command("*IDN?"))

chip = f"{chip}{f'/{subfolder}' if subfolder is not None else ''}/detailed_sweep_{attenuation}dBm"


# total time estimation
total_time = 0
try:
    for power, bandwidth, averages in pow_bw_avg:
        vna_power = power - attenuation

        for num_res in res_of_interest:
            f = fine_peaks[num_res-1]
            frequencies = np.linspace(f-span/2, f+span/2, nop)
            spectrum_measurement = Measurement(operator, chip + f"/Res{num_res}", bandwidth, vna_power, frequencies, averages)
            vna.set_measurement(spectrum_measurement)
            total_time += vna.get_measurement_time()*spectrum_measurement.get_averages()
            # print(f"total time probably in s: {total_time/1000}")
finally:
    vna.rf_off()  # not needed, but safe mechanism
    total_time /= 1000
    d = datetime.today() + timedelta(seconds=total_time)
    string = d.strftime('%H:%M:%S')
    print(f"Start time: {datetime.today().strftime('%H:%M:%S, %a %d.%m.')}")
    print(f"Finish time: {d.strftime('%H:%M:%S, %a %d.%m.')}")


try:
    for power, bandwidth, averages in pow_bw_avg:
        vna_power = power - attenuation

        for num_res in res_of_interest:
            f = fine_peaks[num_res-1]
            frequencies = np.linspace(f-span/2, f+span/2, nop)
            # print(f"Measuring res{num_res} at {power} dB")
            spectrum_measurement = Measurement(operator, chip + f"/Res{num_res}", bandwidth, vna_power, frequencies, averages)
            vna.set_measurement(spectrum_measurement)
            now = datetime.today()
            meas_time = vna.get_measurement_time()*spectrum_measurement.get_averages()/1000
            print(f"Measuring resonance res{num_res} at {power} dB from {now.strftime('%H:%M:%S')} until {(now + timedelta(seconds=meas_time)).strftime('%H:%M:%S')}...")
            vna.rf_on()
            path = vna.measure()
            # print(f"...finished at {datetime.today().strftime('%H:%M:%S')}")
            vna.rf_off()

            fit = notch_port(spectrum_measurement.get_frequencies(), spectrum_measurement.get_data())
            fit.autofit()
            fit.save_fitresults(path)
            fit.plotall(f"D:\\Measurements\\Resonators\\{operator}\\{chip}\\Res{num_res}\\{power}_{averages}avg.pdf")

finally:
    vna.rf_off()
    print(f"Turned off VNA power. Finished at {datetime.today().strftime('%H:%M:%S, %a %d.%m.')}")