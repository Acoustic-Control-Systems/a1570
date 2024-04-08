import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
import logging

from common_functions import *

# set up logging
logger = logging.getLogger()
# create console handler and set level to info
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger.info('Start receiving data from A1570...')

# ip of the device and port
ip: str = '192.168.0.11'
port: int = 5025
rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000 # miliseconds
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

# readout error queue before start
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break

# read IDN string, it returns manufacturer, model, serial number and firmware version
# e.g. 'ACS-Solutions GmbH,A1570,123456789,ESP 1.25 MCU 6.01.244'
idn: str = inst.query('*IDN?')
logger.info(idn)

# set trigger to internal
inst.write('TRIGgering:MODE INTERNAL')
# read back trigger mode (optional)
answ = inst.query('TRIGgering:MODE?')
logger.info(f'Trigger mode: {answ}')
assert 'INTERNAL' == answ, f'Failed on setting the trigger mode to INTERNAL. Received {answ}'

# set internal trigger to 100 ms
inst.write('TRIG:INT 100000 US')
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