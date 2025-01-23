from dataclasses import dataclass
import os
import struct
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
import logging

from common_functions import *

# set up logging
logger = logging.getLogger()
# create console handler and set level to info
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


# Define a data class for block parameters
@dataclass
class BlockParameters:
    gain: int # dB
    pulse_level: int # V
    sampling_rate: int # MHz
    duration: float # number of periods 0.5, 1 ... 8
    averaging: int = 4 # 2^averaging
    probe_frequency: float = 3 # MHz

def save_to_json_file(parameters:BlockParameters, data, filename:str):
    import json
    with open(filename, 'w') as f:
        json.dump({'parameters': parameters.__dict__, 'data': data}, f, indent=4)

def load_from_json_file(filename:str):#->tuple[BlockParameters, b]:
    import json
    with open(filename, 'r') as f:
        data = json.load(f)
        parameters = BlockParameters(**data['parameters'])
        return parameters, data['data']

logger.info('Start receiving data from A1570...')


directory = 'data_blocks'
if not os.path.exists(directory):
    os.makedirs(directory)
    
# ip of the device and port
ip: str = '192.168.0.11'
port: int = 5025
rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000 # miliseconds
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'


tmo = inst.timeout
try:
    inst.timeout = 10  # Set a short timeout
    inst.read_raw()
except visa.errors.VisaIOError:
    # not data to read
    pass
inst.timeout = tmo  # go back to the timeout

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

# disable magnet
inst.write('MAGN:ENAB OFF')
time.sleep(0.5)
# read back magnet state (optional)
answ = inst.query('MAGN:ENAB?')
logger.info(f'Magnet state: {answ}')

# zonder mode to COMBINED
inst.write('ZONDer:MODE COMBINED')
time.sleep(0.5)
# read back magnet state (optional)
answ = inst.query('ZONDer:MODE?')
logger.info(f'Zonder mode: {answ}')


averaging = 4 # 2^averaging
probe_frequency = 3 # MHz
gains_array = [ 0, 5, 10, 15, 20, 25, 30, 35, 40]
pulse_levels = [200, 400, 600]
sampling_rates = [25, 50, 100] 
durations = list(np.arange(0.5, 8.5, 0.5)) #0.5 - 8.0

# set averaging
inst.write(f'AVER:COUN {averaging}')
time.sleep(0.5)
# read back averaging (optional)
answ = inst.query('AVER:COUN?')
logger.info(f'Averaging: {answ}')

# set probe frequency
inst.write(f'TRANsmitter:FREQuency {probe_frequency} MHZ')
time.sleep(0.5)
# read back probe frequency (optional)
answ = inst.query('TRANsmitter:FREQuency?')
logger.info(f'Probe frequency: {answ}')

# iterate over all parameters
for gain in gains_array:
    for pulse_level in pulse_levels:
        for sampling_rate in sampling_rates:
            for duration in durations:
                bp = BlockParameters(gain, pulse_level, sampling_rate, duration, averaging, probe_frequency)

                # set parameters
                inst.write(f'GAIN {gain} DB')
                answ = inst.query(f'GAIN?')
                logger.info(f'Gain: {answ}')
                inst.write(f'TRANsmitter:PULS {pulse_level}')
                answ = inst.query(f'TRANsmitter:PULS?')
                logger.info(f'Pulse level: {answ}')
                inst.write(f'FREQuency {sampling_rate} MHZ')
                answ = inst.query(f'FREQuency?')
                logger.info(f'Sampling rate: {answ}')
                inst.write(f'TRANsmitter:DURation {duration}')
                answ = inst.query(f'TRANsmitter:DURation?')
                logger.info(f'Duration: {answ}')

                # start measurement
                inst.write(f'STAR')
                time.sleep(0.5)

                # read data
                arr = inst.query_binary_values(f'FETC?', 
                                                    datatype='h',
                                                    is_big_endian=False,
                                                    expect_termination=True,
                                                    header_fmt='ieee',
                                                )

                # stop measurement
                inst.write(f'STOP')

                #bytes 16, 17 is vector index
                vector_index = arr[8]
                logger.info(f'Vector index: {vector_index}')

                # cut header of 28 bytes, reverse bytes per word, plot data as 16 bit signed integer
                arr_vector = arr[14:]
                
                save_to_json_file(bp, arr_vector, f'{directory}/block_{gain}_{pulse_level}_{sampling_rate}_{duration}.json')

                # [params,vector] = load_from_json_file(f'{directory}/block_{gain}_{pulse_level}_{sampling_rate}_{duration}.json')


# close connection
inst.close()

# remove stream handler
logger.removeHandler(stream_handler)