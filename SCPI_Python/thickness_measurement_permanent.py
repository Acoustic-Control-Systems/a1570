"""
Automatic thickness measurement example using A1570 EMAT device with permanent magnet probe.

Features:
- SCPI communication setup
- Manual or automatic calibration
- Continuous thickness measurement in automatic mode
- Error queue monitoring

Usage:
1. Set IP address of device
2. Choose calibration mode (manual/automatic)
3. Run script to start measurements
"""

import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
import logging

from common_functions import *

### Logger Setup ###
# Configure logging to show info level messages
logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

### Configuration Parameters ###
# Manual calibration mode:
# True = Interactive calibration during runtime
# False = Use predefined calibration values
is_manual_calibration = True

logger.info('Initialize SCPI for A1570...')

### Device Communication Setup ###
# Network configuration - adjust as needed
ip: str = '192.168.0.11'  # Device IP address
port: int = 5025          # Default SCPI port

# Initialize VISA connection
rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000        # Response timeout in milliseconds
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

### Error Queue Check ###
# Clear any pending errors before starting measurement
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break

### Device Identification ###
# Query device info: manufacturer, model, serial number, firmware
idn: str = inst.query('*IDN?')
logger.info(idn)

# set trigger to internal
inst.write('TRIGgering:MODE INTERNAL')
# read back trigger mode (optional)
answ = inst.query('TRIGgering:MODE?')
logger.info(f'Trigger mode: {answ}')
assert 'INTERNAL' == answ, f'Failed on setting the trigger mode to INTERNAL. Received {answ}'

# set internal trigger to 100 ms
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

# probe type to be used
pt = 'S7394'

# set probe type
inst.write(f'SENSe:PROBe:TYPE "{pt}"')
# read back probe type (optional)
answ = inst.query('SENSe:PROBe:TYPE?')
assert pt == answ, f'Failed on setting the probe type to {pt}. Received {answ}'


### step 1: calibrate probe in air

### option 1: calibrate probe in air to compute dead zones internally
if is_manual_calibration:
    # wait till user confirms that the probe calibration should be started
    input("Calibration step 1. Take the probe in hand and press Enter to continue...")

    # start calibration in air
    inst.write('STAR:CAL:AIR')

    # wait for calibration to finish
    time.sleep(6)

### option 2: set dead zones from top without calibration
else:
    # set dead zones [gain:dead_zone]
    dz = '0:345;5:269;10:226;15:226;20:185;25:236;30:292;35:295;40:295'
    logger.info(f"setting dead zones = '{dz}'")
    inst.write(f"SENSe:DEZones '{dz}'")

# get dead zones after calibration
answ = inst.query('SENSe:DEZones?')
logger.info(f"reading dead zones = {answ}")

dead_zones = parse_dead_zones(answ)
# print line of first terms then a line of second terms, separate each value by a comma
logger.info(','.join([str(dz[0]) for dz in dead_zones]))
logger.info(','.join([str(dz[1]) for dz in dead_zones]))


### step 2: set probe delay

### option 1: calibrate probe on calibration object to compute the probe delay
# ! put the probe to a calibration block prior starting this step
if is_manual_calibration:
    # wait till user confirms that the calibration is done
    input("Calibration step 2. Put the probe on calibration object and press Enter to continue...")

    # start calibration
    inst.write('STAR:CAL:OBJ')

    # wait for calibration to finish
    time.sleep(5)

### option 2: set probe delay from top without calibration
else:
    # set probe delay [us]
    pd = 0.6
    inst.write(f'SENSe:PROBe:DELay:PROCessing {pd}')
    answ = inst.query('SENSe:PROBe:DELay:PROCessing?')
    assert pd == float(answ), f'Failed on setting the probe delay to {pd}. Received {answ}'

# read back probe delay
answ = inst.query('PROB:DEL?')
logger.info(f"Probe delay = {answ}")

# wait till user confirms that the calibration is done
input("Calibration done. Press Enter to continue to start thickness measurements...")

### step 3: measure thickness
# set sound velocity [m/s]
sv = 3247
inst.write(f'SOURce:VELocity:SOUNd {sv}')
answ = inst.query('SOURce:VELocity:SOUNd?')
assert sv == int(answ), f'Failed on setting the sound velocity to {sv}. Received {answ}'
logger.info(f"Sound velocity = {answ}")

last_counter = -1
# sleeping time between result polls
sleeping_time = 2 # seconds
inst.write('STAR:MEAS')
time.sleep(2)
# poll for some time
for i in range(1000):
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


    time.sleep(sleeping_time)

# stop measurement
inst.write('STOP:MEAS')

# close connection
inst.close()
# remove stream handler
logger.removeHandler(stream_handler)