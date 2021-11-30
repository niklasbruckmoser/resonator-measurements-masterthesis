import pyvisa
from PyLab.VNA import VNA

print(pyvisa.ResourceManager().list_resources())
vna = VNA(name='PNA', address='TCPIP0::10.1.1.32::inst0::INSTR')  # Keysight VNA
# vna = VNA(name='PNA', address='TCPIP0::10.1.1.25::inst0::INSTR')  # Keysight VNA

# vna.create_measurement_and_trace(1, "s21_meas", "S21", 1)
vna.run_command("CALC:PAR:SEL 'CH1_S11_1'")