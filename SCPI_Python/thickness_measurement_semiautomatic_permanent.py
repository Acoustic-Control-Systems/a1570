"""
Semi-automatic thickness measurement example using permanent magnet EMAT probe.
This script demonstrates:
- Setting up SCPI communication with A1570
- Configuring strobe parameters for signal processing
- Continuous thickness measurement with signal visualization
- Peak detection using either peak-to-peak or maximum in strobe algorithms
"""

import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
import logging

from common_functions import *

### Device Communication Setup ###
# set up logging
logger = logging.getLogger()
# create console handler and set level to info 
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger.info('Initialize SCPI for A1570...')

# Device network configuration
ip: str = '192.168.0.1'  # Default device IP
port: int = 5025         # Default SCPI port
rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000      # milliseconds - time to wait for device response
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

# Clear error queue before starting
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break

def set_strobe_parameters(strobe_level: int, strobe_begin: int, strobe_width: int):
    """
    Configure signal processing strobe window parameters
    
    Args:
        strobe_level (int): Signal amplitude threshold (0-100%)
        strobe_begin (int): Start position of strobe window (0-8191 samples)
        strobe_width (int): Width of strobe window (0-8191 samples)
        
    Note: The strobe window defines where the algorithm looks for ultrasonic echoes.
    Proper configuration is critical for reliable thickness measurements.
    """
    inst.write(f'SENSe:STROBE:LEVel {strobe_level}')
    answ = inst.query('SENSe:STROBE:LEVel?')
    assert strobe_level == int(answ), f'Failed on setting the strobe level to {strobe_level}. Received {answ}'
    logger.info(f"strobe level = {answ}")
    
    inst.write(f'SENSe:STROBE:BEG {strobe_begin}')
    answ = inst.query('SENSe:STROBE:BEG?')
    assert strobe_begin == int(answ), f'Failed on setting the strobe begin to {strobe_begin}. Received {answ}'
    logger.info(f"strobe begin = {answ}")
    
    inst.write(f'SENSe:STROBE:WIDT {strobe_width}')
    answ = inst.query('SENSe:STROBE:WIDT?')
    assert strobe_width == int(answ), f'Failed on setting the strobe width to {strobe_width}. Received {answ}'
    logger.info(f"strobe width = {answ}")

def get_vector_from_SCPI() -> np.ndarray:
    """
    Fetch A-scan vector data from device using SCPI protocol.
    
    Returns:
        np.ndarray: Array containing A-scan amplitude values.
        Data is returned as 16-bit signed integers.
        
    Note:
        First 14 bytes in raw sigmal contain header information including:
        - Bytes 16-17: Vector index counter
        Actual vector data starts at index 14. Returned vector is 8192 samples long containing the ascan data without header.
    """
    arr = inst.query_binary_values(f'FETCh:ARRay?', 
                                        datatype='h',
                                        is_big_endian=False,
                                    expect_termination=True,
                                    header_fmt='ieee',
                                    )
    #bytes 16, 17 is vector index
    header = arr[:14]
    vector_index = header[8]

    logger.info(f"vector index = {vector_index}, len (header + data) = {len(arr)}")
    
    # cut header of 28 bytes, plot data as 16 bit signed integer
    arr_vector = arr[14:]
    
    return arr_vector

def measurement_strobe_permanent():
    """
    Configure and perform thickness measurement using permanent magnet probe.
    
    Sets up:
    - Probe type (S7694 permanent magnet probe)
    - A-scan vector transmission
    - Signal averaging
    - Measurement parameters
    
    Note: 
        Enabling A-scan vector transmission reduces measurement performance
        but is useful for debugging and setup.
    """
    # Set probe type for permanent magnet EMAT
    pt = 'S7694'
    inst.write(f'SENSe:PROBe:TYPE "{pt}"')
    answ = inst.query('SENSe:PROBe:TYPE?')
    assert pt == answ, f'Failed on setting the probe type to {pt}. Received {answ}'
    
    # Enable A-scan vector transmission
    # Note: This reduces performance but helps with measurement setup
    val = 'ON'
    inst.write('SNDVector '+ val)
    answ = inst.query('SNDVector?')
    assert val == answ, f'Failed enabling sending vector. Received {answ}'

    # Configure signal averaging
    # Valid range: 0-4 (power of 2)
    averaging_power = 4 # 2^4=16
    inst.write(f'SENSe:AVERage:COUNt {averaging_power}')
    answ = inst.query('SENSe:AVERage:COUNt?')
    assert averaging_power == int(answ), f'Failed on setting the averaging power to {averaging_power}. Received {answ}'
    
    # set trigger mode
    mode = 'INTERNAL'
    inst.write(f'TRIG:MODE {mode}')
    answ = inst.query('TRIG:MODE?')
    assert mode == answ, f'Failed on setting the trigger mode to {mode}. Received {answ}'
    
    # set trigger interval
    interval = 0.25 # seconds
    inst.write(f'TRIGgering:INTerval {interval} S')
    answ = inst.query('TRIGgering:INTerval?')
    assert interval == float(answ), f'Failed on setting the trigger interval to {interval}. Received {answ}'
    logger.info(f"set PRR = {interval} s, {1/interval} Hz")
    
    # set sound velocity
    velocity = 3200 # m/s
    inst.write(f'VELocity {velocity}')
    answ = inst.query('VELOcity?')
    assert velocity == int(answ), f'Failed on setting the sound velocity to {velocity}. Received {answ}'

    # set gain
    gain = 15
    inst.write(f'GAIN:LEVel {gain}')
    assert gain == int(inst.query('GAIN:LEVel?')), f'Failed on setting the gain to {gain}'
    
    # readout data from SCPI to clear its buffers
    tmo = inst.timeout
    try:
        inst.timeout = 10  # Set a short timeout
        inst.read_raw()
    except visa.errors.VisaIOError:
        pass
    inst.timeout = tmo  # go back to a timeout of 1 s

    sleeping_time = 0.25 # seconds
    
    # set strobe parameters where processing algorithm searches for the peak(s)
    # examples parameters gives proper result with S7694 probe on 5mm aluminum coin delivered with the device
    strobe_level = 15 # 0-100%
    strobe_begin = 140 # 0-8191 samples
    strobe_width = 250 # 0-8191 samples
    
    set_strobe_parameters(strobe_level, strobe_begin, strobe_width)

    ## select algorithm to start:
    # peak to peak algorithm
    # inst.write('STAR:P2Peak')            
    # maximum in strobe algorithm
    inst.write('STAR:MAXStrobe')

    last_counter = -1
    # loop for some time
    for i in range(10):

        answ = inst.query('FETCh:RESult:MEASure?')
        
        result_obj = parse_measurement_result(answ)
        # if new thickness is available, device will increment counter in result class 
        # process thickness if the counter changed
        if last_counter != result_obj.counter:
            last_counter = result_obj.counter
            if( not result_obj.contact or
                result_obj.thickness==65535 or result_obj.thickness==-1):
                logger.info(f"no thickness found")
            else:
                logger.info(f"thickness = {result_obj.thickness}mm")


        arr_vector = get_vector_from_SCPI()
        plt.plot(arr_vector)
        plt.show()

        time.sleep(sleeping_time)        

    # stop measurement
    inst.write('STOP')


if __name__ == '__main__':
    # read IDN string, it returns manufacturer, model, serial number and firmware version
    # e.g. 'ACS-Solutions GmbH,A1570,123456789,ESP 1.25 MCU 6.01.244'
    idn: str = inst.query('*IDN?')
    logger.info(idn)

    measurement_strobe_permanent()

    inst.close()
    logger.info('End of the script')