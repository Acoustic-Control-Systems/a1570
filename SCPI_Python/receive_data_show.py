"""
Example script for receiving and visualizing raw A-scan data from A1570 EMAT device.

Features:
- Establishes SCPI connection to device
- Configures internal triggering 
- Fetches raw A-scan vectors
- Displays signal using matplotlib

Usage:
1. Configure device IP address
2. Run script to capture and display single A-scan
3. Close plot window to end program
"""

### Imports and Logger Setup ###
import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
import logging

from common_functions import *

# Configure logging to show info level messages
logger = logging.getLogger()
logger.level = logging.INFO  
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger.info('Start receiving data from A1570...')

### Device Configuration ###
# Network settings - adjust IP as needed for your device
ip: str = '192.168.0.2'  # Device IP address
port: int = 5025         # Default SCPI port

# Initialize VISA connection
rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000      # Timeout in milliseconds
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

# Clear error queue before starting measurement
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break

# Query device identification
idn: str = inst.query('*IDN?')  # Returns: manufacturer,model,serial,firmware
logger.info(idn)

# Configure internal trigger mode for autonomous operation
inst.write('TRIGgering:MODE INTERNAL')
# read back trigger mode (optional)
answ = inst.query('TRIGgering:MODE?')
logger.info(f'Trigger mode: {answ}')
assert 'INTERNAL' == answ, f'Failed on setting the trigger mode to INTERNAL. Received {answ}'

# set internal trigger to 250 ms
inst.write('TRIG:INT 250000 US')
time.sleep(0.5)
# read back trigger interval (optional)
answ = inst.query('TRIGgering:INTerval?')
logger.info(f'Trigger interval: {answ} seconds')

# enable transmitter
inst.write('TRAN:ENAB ON')
time.sleep(0.5)
# read back transmitter state (optional)
answ = inst.query('TRAN:ENAB?')
logger.info(f'Transmitter state: {answ}')

# start measurement
inst.write(f'STAR')
time.sleep(0.5)

# read data
arr = inst.query_binary_values(f'FETC?', 
                                    datatype='h',
                                    is_big_endian=False,
                                    expect_termination=False,
                                    header_fmt='ieee',
                                )

# stop measurement
inst.write(f'STOP')

# close connection
inst.close()

#bytes 16, 17 is vector index
vector_index = arr[8]
logger.info(f'Vector index: {vector_index}')

# cut header of 28 bytes, reverse bytes per word, plot data as 16 bit signed integer
arr_vector = arr[14:]

plt.plot(arr_vector)
plt.show()

# remove stream handler
logger.removeHandler(stream_handler)