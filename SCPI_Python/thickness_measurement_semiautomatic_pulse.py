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
inst:visa.Resource = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000      # milliseconds - time to wait for device response
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

# Clear error queue before starting
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break



def measurement_strobe_pulse():
    """
    Configure and perform thickness measurement using permanent magnet probe.
    
    Sets up:
    - Probe type (S3850 pulse magnet probe)
    - A-scan vector transmission
    - Signal averaging
    - Measurement parameters
    
    Note: 
        Enabling A-scan vector transmission reduces measurement performance
        but is useful for debugging and setup.
        
        Prior performing measurements, ensure the probe is properly connected, batteries are inserted, and the probe is calibrated (in air and on object).
    """
    # Set probe type for permanent magnet EMAT
    pt = 'S3850'
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
    # examples parameters gives proper result with S3850 probe on 5mm aluminum coin delivered with the device
    strobe_level = 20 # 0-100%
    strobe_begin = 300 # 0-8191 samples
    strobe_width = 400 # 0-8191 samples
    
    set_strobe_parameters(inst, strobe_level, strobe_begin, strobe_width)

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


        arr_vector = get_vector_from_SCPI(inst)
        plt.plot(arr_vector)
        plt.show()
        # request temperature of the EMAT probe
        # it is not necessary to check the temperature every time
        # it can be done once per minute or so
        answ = inst.query('STATus:PROBe:TEMPerature?')
        # temperature is in Celsius degrees
        temperature = float(answ)
        # very low temperature may indicate that the pulse magnet probe is not connected to the device
        if temperature < -60:
            logger.warning(f"Probe temperature = {temperature}°C. Check probe connection.")
        else:
            # check if the temperature is too high
            temperatureWarning = 50 # warning threshold, when the measurement is slowed down
            temperatureError = 75 # error threshold, when the measurement is stopped automatically by the device
            # log the temperature
            if temperature > temperatureError:
                logger.warning(f"Probe temperature = {temperature}°C. No measurements possible until the probe cooled down.")
            elif temperature > temperatureWarning:
                logger.warning(f"Probe temperature = {temperature}°C. Measurements will be slowed down.")
            else:
                logger.info(f"Probe temperature = {temperature}°C.")            

        time.sleep(sleeping_time)        

    # stop measurement
    inst.write('STOP')


if __name__ == '__main__':
    # read IDN string, it returns manufacturer, model, serial number and firmware version
    # e.g. 'ACS-Solutions GmbH,A1570,123456789,ESP 1.25 MCU 6.01.244'
    idn: str = inst.query('*IDN?')
    logger.info(idn)

    measurement_strobe_pulse()

    inst.close()
    logger.info('End of the script')