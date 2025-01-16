import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
import logging

from common_functions import *

### initializing
# set up logging
logger = logging.getLogger()
# create console handler and set level to info
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# switch to True if you want to calibrate manually or False to set calibration values from top without calibration
is_manual_calibration = True

logger.info('Initialize SCPI for A1570...')

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
pt = 'S3850'

# set probe type
inst.write(f'SENSe:PROBe:TYPE "{pt}"')
# read back probe type (optional)
answ = inst.query('SENSe:PROBe:TYPE?')
assert pt == answ, f'Failed on setting the probe type to {pt}. Received {answ}'


### step 1: calibrate probe in air

## option 1: calibrate probe in air to compute dead zones, eddy array and noise parameters internally
if is_manual_calibration:
    # wait till user confirms that the probe calibration should be started
    input("Calibration step 1. Take the probe in hand and press Enter to continue...")

    # start calibration in air
    inst.write('STAR:CAL:AIR')

    # wait for calibration to finish
    time.sleep(6)

## option 2: set parameters from top without calibration
else:
    # set dead zones [gain:dead_zone]
    dz = '0:345;5:269;10:226;15:226;20:185;25:236;30:292;35:295;40:295'
    logger.info(f"setting dead zones = '{dz}'")
    inst.write(f"SENSe:DEZones '{dz}'")

    # set noise parameters
    # {"command" : "noise_function", "noise_end" : 700, "noise_level" : 818, "noise_start" : 400}
    import json
    json_str = json.dumps(
        {"command" : "noise_function",
        "noise_end" : 700,
        "noise_level" : 818,
        "noise_start" : 400})
    logger.info(f"setting noise parameters = {json_str}")
    inst.write(f'SENSe:CALibration:NOISe {json_str}')
    time.sleep(0.1)             

    # set eddy parameters
    import json
    json_str = json.dumps( 
        {"command" : "calibration_eddy_array",
        "eddy" : [37, 58, 74, 87, 98, 108, 115, 121, 124, 124, 122, 116, 107, 95, 83, 73, 65, 59, 55, 53, 50, 44, 39, 35, 30, 26, 20, 15, 9, 5, 1, -1, -4, -6, -8, -9, -10, -11, -11, -12, -12, -12, -13, -13, -13, -13, -13, -13, -13, -12, -12, -11, -11, -10, -10, -9, -8, -8, -7, -7, -6, -6, -5, -5], 
        "eddy_start" : 42})
    logger.info(f"setting eddy calibration array = {json_str}")
    inst.write(f'SENSe:CALibration:EDARray \'{json_str}\'')
    time.sleep(0.1)             


## read back calibration parameters (optional)
# get noise parameters
answ = inst.query('SENSe:CALibration:NOISe?')
print(f"noise parameters = {answ}")

# get eddy calibration array
answ = inst.query('SENSe:CALibration:EDARray?')
print(f"read back eddy calibration array = {answ}")

# get dead zones after calibration
answ = inst.query('SENSe:DEZones?')
logger.info(f"reading dead zones = {answ}")

dead_zones = parse_dead_zones(answ)
# print line of first terms then a line of second terms, separate each value by a comma
logger.info(','.join([str(dz[0]) for dz in dead_zones]))
logger.info(','.join([str(dz[1]) for dz in dead_zones]))




### step 2: set probe delay

## option 1: calibrate probe on calibration object to compute the probe delay
# ! put the probe to a calibration block prior starting this step
if is_manual_calibration:
    # wait till user confirms that the calibration is done
    input("Calibration step 2. Put the probe on calibration object and press Enter to continue...")
    # start calibration
    inst.write('STAR:CAL:OBJ')

    # wait for calibration to finish
    time.sleep(5)

## option 2: set probe delay manually
else:
    # set probe delay [us]
    pd = 0.21
    inst.write(f'SENSe:PROBe:DELay:PROCessing {pd}')
    answ = inst.query('SENSe:PROBe:DELay:PROCessing?')
    assert pd == float(answ), f'Failed on setting the probe delay to {pd}. Received {answ}'

## read back probe delay (optional)
answ = inst.query('PROB:DEL?')
logger.info(f"Probe delay = {answ}")

# wait till user confirms that the calibration is done
input("Calibration done. Press Enter to continue to start thickness measurements...")

### step 3: measure thickness
## set sound velocity [m/s]
sv = 3247
inst.write(f'SOURce:VELocity:SOUNd {sv}')
answ = inst.query('SOURce:VELocity:SOUNd?')
assert sv == int(answ), f'Failed on setting the sound velocity to {sv}. Received {answ}'
logger.info(f"Sound velocity = {answ}")

## set software averaging (optional)
swa = 13 # number of software averages (1-100)
inst.write(f'SENSe:SOAVerage:COUNt {swa}')
# read back software averaging (optional)
answ = inst.query('SENSe:SOAVerage:COUNt?')
assert swa == int(answ), f'Failed on setting the software averaging to {swa}. Received {answ}'
logger.info(f"software averaging = {answ}")

# enable software averaging
inst.write(f'SENSe:SOAVerage:ENAB ON')
# read back software averaging enable (optional)
answ = inst.query('SENSe:SOAVerage:ENAB?')
assert 'ON' == answ, f'Failed on setting the software averaging enable to ON. Received {answ}'


# poll result for some time
last_counter = -1
# sleeping time between result polls
sleeping_time = 2 # seconds

# set internal trigger to 1 s (for pulse magnet it is recommended to reduce the trigger interval to prevent fast overheating of the probe)
inst.write('TRIG:INT 0.25 S')
time.sleep(0.5)
# read back trigger interval (optional)
answ = inst.query('TRIGgering:INTerval?')
logger.info(f'Trigger interval: {answ} seconds')

inst.write('STAR:MEAS')
time.sleep(2)
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

    time.sleep(sleeping_time)

# stop measurement
inst.write('STOP:MEAS')

# close connection
inst.close()
# remove stream handler
logger.removeHandler(stream_handler)