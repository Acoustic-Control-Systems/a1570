import sys
import time
import unittest

import numpy as np
import pyvisa as visa
import logging

from common_functions import *
logger = logging.getLogger()
logger.level = logging.INFO

class test_scpi_interface_a1570(unittest.TestCase):
    trasmitter_frequencies = np.array([20, 20000]) * 1000
    trasmitter_frequencies_step = 1000 * 1000
    trasmitter_periods = np.array([10, 250]) * 1E-9
    trasmitter_periods_step = 10 * 1E-9
    on_off_modes = {
            'OFF',
            'ON',
        }        
    
    stream_handler = logging.StreamHandler(sys.stdout)
    
    def setUp(self) -> None:
        
        logger.addHandler(self.stream_handler)
        logger.info('Start test_scpi_interface_a1570...')

        self.ip: str = '192.168.0.11'
        self.port: int = 5025
        self.rm = visa.ResourceManager()
        self.inst = self.rm.open_resource(f'tcpip::{self.ip}::{str(self.port)}::SOCKET')
        self.inst.encoding = 'iso-8859-1'
        self.inst.timeout = 5000 # miliseconds
        self.inst.read_termination = '\r\n'
        self.inst.write_termination = '\r\n'
        
        self.idn: str = self.inst.query('*IDN?')
        logger.info(self.idn)

        # readout error queue before test
        while True:
            err_num, err_msg = read_error_queue(self.inst)
            if (err_num == 0):
                break

    def tearDown(self) -> None:
        self.inst.close()
        logger.removeHandler(self.stream_handler)

    def test_connection(self):
        idn = self.inst.query('*IDN?')
        assert idn.startswith('ACS-Solutions GmbH,A1570')

    def test_getters(self):
        answ = self.inst.query('SOURce:GAIN:LEVel?')
        logger.info(f"gain = {answ}")
        answ = self.inst.query('SOURce:STARt?')
        logger.info(f"start = {answ}")
        answ = self.inst.query('SOURce:TRIGgering:INTerval?')
        logger.info(f"interval = {answ}")
        answ = self.inst.query('SOURce:TRIGgering:MODE?')
        logger.info(f"mode = {answ}")
        answ = self.inst.query('SOURce:FREQuency?')
        logger.info(f"frequency = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:PULSe:LEVel?')
        logger.info(f"pulse level = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:FREQuency?')
        logger.info(f"frequency = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:PERIod?')
        logger.info(f"period = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:DURation?')
        logger.info(f"duration = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:ENABle?')
        logger.info(f"enable = {answ}")
        answ = self.inst.query('SOURce:TRANsmitter:MODE?')
        logger.info(f"mode = {answ}")
        answ = self.inst.query('SOURce:DATA:LENGth?')
        logger.info(f"data length = {answ}")
        answ = self.inst.query('SENSe:AVERage:COUNt?')
        logger.info(f"average count = {answ}")
        answ = self.inst.query('SENSe:AVERage:PERIod?')
        logger.info(f"average period = {answ}")
        answ = self.inst.query('SENSe:AVERage:PERIod:RANDom?')
        logger.info(f"average period random = {answ}")
        answ = self.inst.query('SENSe:FILTer:HPASs:NUMBer?')
        logger.info(f"filter hpass number = {answ}")
        answ = self.inst.query('SENSe:MAGNet:DELay?')
        logger.info(f"magnet delay = {answ}")
        answ = self.inst.query('SENSe:MAGNet:ENABle?')
        logger.info(f"magnet enable = {answ}")
        answ = self.inst.query('SENSe:MAGNet:VOLTage?')
        logger.info(f"magnet voltage = {answ}")
        answ = self.inst.query('STATus:BATTery?')
        logger.info(f"battery = {answ}")
        answ = self.inst.query('STATus:CHSTatus?')
        logger.info(f"channel status = {answ}")

    def test_setters(self):
        self.inst.write('SOURce:GAIN:LEVel 0')
        answ = self.inst.query('SOURce:GAIN:LEVel?')
        logger.info(f"gain = {answ}")
        self.inst.write('SOURce:TRIGgering:INTerval 1000000 US')
        answ = self.inst.query('SOURce:TRIGgering:INTerval?')
        logger.info(f"interval = {answ}")
        self.inst.write('SOURce:TRIGgering:MODE INTERNAL')
        answ = self.inst.query('SOURce:TRIGgering:MODE?')
        logger.info(f"mode = {answ}")
        self.inst.write('SOURce:FREQuency 25')
        answ = self.inst.query('SOURce:FREQuency?')
        logger.info(f"frequency = {answ}")
        self.inst.write('SOURce:TRANsmitter:PULSe:LEVel 200')
        answ = self.inst.query('SOURce:TRANsmitter:PULSe:LEVel?')
        logger.info(f"pulse level = {answ}")
        self.inst.write('SOURce:TRANsmitter:FREQuency 3000')
        answ = self.inst.query('SOURce:TRANsmitter:FREQuency?')
        logger.info(f"frequency = {answ}")
        self.inst.write('SOURce:TRANsmitter:PERIod 100')
        answ = self.inst.query('SOURce:TRANsmitter:PERIod?')
        logger.info(f"period = {answ}")
        self.inst.write('SOURce:TRANsmitter:DURation 2')
        answ = self.inst.query('SOURce:TRANsmitter:DURation?')
        logger.info(f"duration = {answ}")
        self.inst.write('SOURce:TRANsmitter:ENABle OFF')
        answ = self.inst.query('SOURce:TRANsmitter:ENABle?')
        logger.info(f"enable = {answ}")
        self.inst.write('SOURce:TRANsmitter:MODE OFF')
        answ = self.inst.query('SOURce:TRANsmitter:MODE?')
        logger.info(f"mode = {answ}")
        self.inst.write('SOURce:DATA:LENGth 1024')
        answ = self.inst.query('SOURce:DATA:LENGth?')
        logger.info(f"data length = {answ}")
        self.inst.write('SENSe:AVERage:COUNt 0')
        answ = self.inst.query('SENSe:AVERage:COUNt?')
        logger.info(f"average count = {answ}")
        self.inst.write('SENSe:AVERage:PERIod 10')
        answ = self.inst.query('SENSe:AVERage:PERIod?')
        logger.info(f"average period = {answ}")
        self.inst.write('SENSe:AVERage:PERIod:RANDom 10')
        answ = self.inst.query('SENSe:AVERage:PERIod:RANDom?')
        logger.info(f"average period random = {answ}")
        self.inst.write('SENSe:FILTer:HPASs:NUMBer 4')
        answ = self.inst.query('SENSe:FILTer:HPASs:NUMBer?')
        logger.info(f"filter hpass number = {answ}")
        self.inst.write('SENSe:MAGNet:DELay 10')
        answ = self.inst.query('SENSe:MAGNet:DELay?')
        logger.info(f"magnet delay = {answ}")
        self.inst.write('SENSe:MAGNet:ENABle OFF')
        answ = self.inst.query('SENSe:MAGNet:ENABle?')
        logger.info(f"magnet enable = {answ}")
        self.inst.write('SENSe:MAGNet:VOLTage 15')
        answ = self.inst.query('SENSe:MAGNet:VOLTage?')
        logger.info(f"magnet voltage = {answ}")

    def test_receiving_data(self):

        header_size = 14 #words (2 bytes)

        self.inst.write('SOURce:TRIGgering:INTerval 100000 US')
        time.sleep(0.5)
        self.inst.write(f'SOURce:STARt')
        time.sleep(1)

        for i in range(10):
            tmo = self.inst.timeout
            try:
                self.inst.timeout = 10  # Set a short timeout
                self.inst.read_raw()
            except visa.errors.VisaIOError:
                pass
            self.inst.timeout = tmo  # go back to a timeout of 1 s

            arr = self.inst.query_binary_values(f'FETCh:ARRay?', 
                                                datatype='h',
                                                is_big_endian=False,
                                            expect_termination=True,
                                            header_fmt='ieee',
                                            )
            #bytes 16, 17 is vector index
            header = arr[:header_size]
            vector_index = header[8]

            logger.info(f"vector index = {vector_index}, len (header + data) = {len(arr)}")

        self.inst.write(f'SOURce:STOP')

    def test_gain_wrong_int(self):
        self.inst.write(f'SOURce:GAIN -50')
        check_error_queue_and_assert_if_no_error(self.inst)

    def test_gain_wrong_float(self):
        self.inst.write(f'SOURce:GAIN 0.5 DB')
        check_error_queue_and_assert_if_no_error(self.inst)

    def test_gain_wrong_units(self):
        self.inst.write(f'GAIN 20 V')
        check_error_queue_and_assert_if_no_error(self.inst)

    def test_gain_q(self):
        g1 = self.inst.query('GAIN?')
        g2 = self.inst.query('SOUR:GAIN?')
        g3 = self.inst.query(':SOUR:GAIN?')
        g4 = self.inst.query('SOURce:GAIN?')
        g5 = self.inst.query('SOURce:GAIN:LEVel?')
        g6 = self.inst.query('SOUR:GAIN:LEV?')
        assert g2 == g4 == g5 == g6, f'Failed on query the gain. Received {g2} {g4} {g5} {g6}'

    def test_gain(self):
        gain = self.inst.query('GAIN?')  # save
        gain = 10
        self.inst.write('GAIN 0')
        self.inst.write(f'GAIN {gain}')
        rg = int(self.inst.query('GAIN?'))
        self.inst.write(f'GAIN {gain}')  # restore
        assert gain == rg

    def test_gain_units(self):
        gain = self.inst.query('GAIN?')  # save
        g = 10
        self.inst.write('GAIN 0')
        self.inst.write(f'GAIN {g} DB')
        rg = int(self.inst.query('GAIN?'))
        self.inst.write(f'GAIN {gain}')  # restore
        assert g == rg, f'Failed on setting the gain to {g} dB with units. Received {rg}'

    def test_gain_whole_range(self):
        gain = self.inst.query('SOUR:GAIN?') # save
        for g in range(0, 40, 1):
            self.inst.write(f'SOUR:GAIN {g}')
            rg = int(self.inst.query('SOUR:GAIN?'))
            assert rg == g, f'Failed on setting the gain to {g} dB. Received {rg}'
        self.inst.write(f'GAIN {gain}') # restore

    def test_gain_min(self):
        gain = self.inst.query('SOUR:GAIN?')  # save
        gmin = 0
        self.inst.write(f'SOUR:GAIN MIN')
        r = int(self.inst.query('SOUR:GAIN?'))
        assert r == gmin, f'Failed on setting the gain to MIN ({gmin}) dB. Received {r}'
        self.inst.write(f'SOUR:GAIN {gain} DB')  # restore

    def test_gain_max(self):
        gain = self.inst.query('SOUR:GAIN?')  # save
        gmax = 40
        self.inst.write(f'SOUR:GAIN MAX')
        r = int(self.inst.query('SOUR:GAIN?'))
        assert r == gmax, f'Failed on setting the gain to MAX ({gmax}) dB. Received {r}'
        self.inst.write(f'SOUR:GAIN {gain}')  # restore

    def test_gain_up(self):
        gain = self.inst.query('SOUR:GAIN?')  # save
        g = 0
        self.inst.write(f'SOUR:GAIN {g}')
        self.inst.write(f'SOUR:GAIN UP')
        r = int(self.inst.query('SOUR:GAIN?'))
        assert r == g+1, f'Failed on setting the gain to UP ({g}+1) dB. Received {r}'
        self.inst.write(f'SOUR:GAIN {gain}')  # restore

    def test_gain_down(self):
        gain = self.inst.query('SOUR:GAIN?')  # save
        g = 10
        self.inst.write(f'SOUR:GAIN {g}')
        self.inst.write(f'SOUR:GAIN DOWN')
        r = int(self.inst.query('SOUR:GAIN?'))
        assert r == g-1, f'Failed on setting the gain to DOWN ({g}-1) dB. Received {r}'
        self.inst.write(f'SOUR:GAIN {gain}')  # restore

    def test_gain_defualt(self):
        gain = self.inst.query('SOUR:GAIN?')  # save
        g = 0
        self.inst.write(f'SOUR:GAIN DEFAULT')
        r = int(self.inst.query('SOUR:GAIN?'))
        assert r == g, f'Failed on setting the gain to DEFAULT ({g}) dB. Received {r}'
        self.inst.write(f'SOUR:GAIN {gain}')  # restore

    def test_triggering_interval(self):
        intervals = np.array([10000, 100000, 1000000]) * 1E-6
        for interval in intervals:
            self.inst.write(f'TRIGgering:INTerval {interval} S')
            r = float(self.inst.query('TRIGgering:INTerval?'))
            check_error_queue_and_assert(self.inst)
            assert abs(r-interval)<=1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # us
        interval = min(intervals)
        self.inst.write(f'TRIGgering:INTerval {interval* 1E6} US')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval) <= 1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # min
        interval = min(intervals)
        self.inst.write(f'TRIGgering:INTerval MINimum')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval) <= 1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # max
        interval = max(intervals)
        self.inst.write(f'TRIGgering:INTerval MAXimum')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval) <= 1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # def
        interval = 0.1
        self.inst.write(f'TRIGgering:INTerval DEFault')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval) <= 1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # step
        step_s = 10000*1E-6
        # up
        interval = min(intervals)
        interval_r = interval + step_s
        self.inst.write(f'TRIGgering:INTerval {interval} S')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        self.inst.write(f'TRIGgering:INTerval UP')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval_r) <= 1E-6, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'
        # down
        interval = max(intervals)
        interval_r = interval - step_s
        self.inst.write(f'TRIGgering:INTerval {interval} S')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        self.inst.write(f'TRIGgering:INTerval DOWN')
        r = float(self.inst.query('TRIGgering:INTerval?'))
        assert abs(r - interval_r) <= 1E-4, f'Failed on setting the triggering interval ({interval}) s. Received {r} s'

    def test_trasmitter_pulse(self):
        pulses = [200, 400, 600]
        for pulse in pulses:
            self.inst.write(f'TRANsmitter:PULSe {pulse} V')
            r = float(self.inst.query('TRANsmitter:PULSe?'))
            check_error_queue_and_assert(self.inst)
            assert r == pulse, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'
        # min
        pulse = min(pulses)
        self.inst.write(f'TRANsmitter:PULSe MINimum')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        assert r == pulse, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'
        # max
        pulse = max(pulses)
        self.inst.write(f'TRANsmitter:PULSe MAXimum')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        assert r == pulse, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'
        # def
        pulse = 200
        self.inst.write(f'TRANsmitter:PULSe DEFault')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        assert r == pulse, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'
        # up
        pulse = min(pulses)
        interval_must_value = pulses[1]
        self.inst.write(f'TRANsmitter:PULSe {pulse} V')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        self.inst.write(f'TRANsmitter:PULSe UP')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        assert r == interval_must_value, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'
        # down
        pulse = pulses[1]
        interval_must_value = pulses[0]
        self.inst.write(f'TRANsmitter:PULSe {pulse} V')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        self.inst.write(f'TRANsmitter:PULSe DOWN')
        r = float(self.inst.query('TRANsmitter:PULSe?'))
        assert r == interval_must_value, f'Failed on setting the transmitter pulse ({pulse}) V. Received {r} V'

    def _get_int(self, query):
        return int(float(self.inst.query(query)))

    def _get_float(self, query):
        q_str = self.inst.query(query)
        return float(q_str)

    def test_trasmitter_frequency(self):
        freqs = self.trasmitter_frequencies
        freqs_step = self.trasmitter_frequencies_step
        frequencies = list(range(freqs[0], freqs[1], freqs_step))
        frequencies.append(freqs[1])
        for frequency in frequencies:
            self.inst.write(f'TRANsmitter:FREQuency {frequency} HZ')
            r = self._get_int('TRANsmitter:FREQuency?')
            check_error_queue_and_assert(self.inst)
            # TODO realy huge number bellow (something wrong with device)
            assert abs(r - frequency) <= 2000000, f'Failed on setting the transmitter frequency ({frequency}) Hz. Received {r} Hz'
            # time.sleep(1)
        # min
        frequency = min(frequencies)
        self.inst.write(f'TRANsmitter:FREQuency MINimum')
        r = self._get_int('TRANsmitter:FREQuency?')
        assert r == frequency, f'Failed on setting the transmitter frequency ({frequency}) Hz. Received {r} Hz'
        # max
        frequency = max(frequencies)
        self.inst.write(f'TRANsmitter:FREQuency MAXimum')
        r = self._get_int('TRANsmitter:FREQuency?')
        assert r == frequency, f'Failed on setting the transmitter frequency ({frequency}) Hz. Received {r} Hz'
        # def
        frequency = 5000000
        self.inst.write(f'TRANsmitter:FREQuency DEFault')
        r = self._get_int('TRANsmitter:FREQuency?')
        assert r == frequency, f'Failed on setting the transmitter frequency ({frequency}) Hz. Received {r} Hz'
        # step
        step_hz = 1000
        # up
        frequency = min(frequencies)
        frequency_must_value = frequency + step_hz
        self.inst.write(f'TRANsmitter:FREQuency {frequency} HZ')
        self.inst.write(f'TRANsmitter:FREQuency UP')
        r = self._get_int('TRANsmitter:FREQuency?')
        # TODO realy huge number bellow (something wrong with device)
        assert abs(r -frequency_must_value) <= 5*step_hz, f'Failed on setting the transmitter frequency ({frequency_must_value}) Hz. Received {r} Hz'
        # down
        frequency = frequencies[1]
        frequency_must_value = frequency - step_hz
        self.inst.write(f'TRANsmitter:FREQuency {frequency} HZ')
        self.inst.write(f'TRANsmitter:FREQuency DOWN')
        r = self._get_int('TRANsmitter:FREQuency?')
        # TODO realy huge number bellow (something wrong with device)
        assert abs(r -frequency_must_value) <= step_hz, f'Failed on setting the transmitter frequency ({frequency_must_value}) Hz. Received {r} Hz'

    def test_trasmitter_period(self):
        pers = self.trasmitter_periods
        pers_step = self.trasmitter_periods_step
        periods = list(np.arange(pers[0], pers[1], pers_step))
        periods.append(pers[1])
        # print(periods)
        for period in periods:
            self.inst.write(f'TRANsmitter:PERiod {period} S')
            r = self._get_float('TRANsmitter:PERiod?')
            check_error_queue_and_assert(self.inst)
            assert abs(r - period) <= 1500E-9, f'Failed on setting the transmitter period ({period}) s. Received {r} s'
            time.sleep(0.5)

        # min
        period = min(periods)
        self.inst.write(f'TRANsmitter:PERiod MINimum')
        r = self._get_float('TRANsmitter:PERiod?')
        assert abs(r - period) <= 20E-9, f'Failed on setting the transmitter period ({period}) s. Received {r} s'
        time.sleep(0.5)

        # max
        period = max(periods)
        self.inst.write(f'TRANsmitter:PERiod MAXimum')
        r = self._get_float('TRANsmitter:PERiod?')
        assert abs(r - period) <= 20E-9, f'Failed on setting the transmitter period ({period}) s. Received {r} s'
        time.sleep(0.5)

        # def
        period = 140E-9
        self.inst.write(f'TRANsmitter:PERiod DEFault')
        r = self._get_float('TRANsmitter:PERiod?')
        assert abs(r - period) <= 20E-9, f'Failed on setting the transmitter period ({period}) s. Received {r} s'
        time.sleep(0.5)

        # up
        period = periods[0]
        period_must_value = periods[1]
        self.inst.write(f'TRANsmitter:PERiod {period} S')
        self.inst.write(f'TRANsmitter:PERiod UP')
        check_error_queue_and_assert(self.inst)
        r = self._get_float('TRANsmitter:PERiod?')
        assert abs(r - period_must_value) <= 20E-9, f'Failed on setting the transmitter period ({period_must_value}) s. Received {r} s'
        time.sleep(0.5)

        # down
        period = periods[1]
        period_must_value = periods[0]
        self.inst.write(f'TRANsmitter:PERiod {period} S')
        self.inst.write(f'TRANsmitter:PERiod DOWN')
        r = self._get_float('TRANsmitter:PERiod?')
        assert abs(r - period_must_value) <= 20E-9, f'Failed on setting the transmitter period ({period_must_value}) s. Received {r} s'
        time.sleep(0.5)

    def test_trasmitter_duration(self):
        durations = list(np.arange(0.5, 8.5, 0.5)) #0.5 - 8.0
        for duration in durations:
            self.inst.write(f'TRANsmitter:DURation {duration}')
            r = self._get_float('TRANsmitter:DURation?')
            check_error_queue_and_assert(self.inst)
            assert r == duration, f'Failed on setting the transmitter duration ({duration}). Received {r}'

        # min
        duration = min(durations)
        self.inst.write(f'TRANsmitter:DURation MINimum')
        r = self._get_float('TRANsmitter:DURation?')
        assert r == duration, f'Failed on setting the transmitter duration ({duration}). Received {r}'

        # max
        duration = max(durations)
        self.inst.write(f'TRANsmitter:DURation MAXimum')
        r = self._get_float('TRANsmitter:DURation?')
        assert r == duration, f'Failed on setting the transmitter duration ({duration}). Received {r}'

        # def
        duration = min(durations)
        self.inst.write(f'TRANsmitter:DURation DEFault')
        r = self._get_float('TRANsmitter:DURation?')
        assert r == duration, f'Failed on setting the transmitter duration ({duration}). Received {r}'

        # step
        step = 0.5

        # up
        duration = min(durations)
        duration_must_value = duration + step
        self.inst.write(f'TRANsmitter:DURation {duration}')
        self.inst.write(f'TRANsmitter:DURation UP')
        r = self._get_float('TRANsmitter:DURation?')
        assert r == duration_must_value, f'Failed on setting the transmitter duration ({duration}). Received {r}'

        # down
        duration = max(durations)
        duration_must_value = duration - step
        self.inst.write(f'TRANsmitter:DURation {duration}')
        self.inst.write(f'TRANsmitter:DURation DOWN')
        r = self._get_float('TRANsmitter:DURation?')
        assert r == duration_must_value, f'Failed on setting the transmitter duration ({duration}). Received {r}'

    def test_sampling_frequency(self):
        frequencies = np.array([25, 50, 100]) * 1E+6
        for frequency in frequencies:
            self.inst.write(f'FREQuency {frequency} HZ')
            r = self._get_int('FREQuency?')
            check_error_queue_and_assert(self.inst)
            assert abs(r - frequency) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'
        # min
        frequency = min(frequencies)
        self.inst.write(f'FREQuency MINimum')
        r = self._get_int('FREQuency?')
        assert abs(r - frequency) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'
        # max
        frequency = max(frequencies)
        self.inst.write(f'FREQuency MAXimum')
        r = self._get_int('FREQuency?')
        assert abs(r - frequency) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'
        # def
        frequency = 100E+6
        self.inst.write(f'FREQuency DEFault')
        r = self._get_int('FREQuency?')
        assert abs(r - frequency) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'
        # up
        frequency = frequencies[0]
        frequency_must_value = frequencies[1]
        self.inst.write(f'FREQuency {frequency} HZ')
        self.inst.write(f'FREQuency UP')
        r = self._get_int('FREQuency?')
        assert abs(r - frequency_must_value) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'
        # down
        frequency = frequencies[1]
        frequency_must_value = frequencies[0]
        self.inst.write(f'FREQuency {frequency} HZ')
        self.inst.write(f'FREQuency DOWN')
        r = self._get_int('FREQuency?')
        assert abs(r - frequency_must_value) <= 1, f'Failed on setting the sampling frequency ({frequency}) Hz. Received {r} Hz'

    def test_average_count(self):
        counts = range(0, 14, 1) #excluding 14
        for count in counts:
            self.inst.write(f'SENSe:AVERage:COUNt {count}')
            r = self._get_int('SENSe:AVERage:COUNt?')
            check_error_queue_and_assert(self.inst)
            assert r == count, f'Failed on setting the average count ({count}). Received {r}'

        # min
        count = min(counts)
        self.inst.write(f'SENSe:AVERage:COUNt MINimum')
        r = self._get_int('SENSe:AVERage:COUNt?')
        assert r == count, f'Failed on setting the average count ({count}). Received {r}'

        # max
        count = max(counts)
        self.inst.write(f'SENSe:AVERage:COUNt MAXimum')
        r = self._get_int('SENSe:AVERage:COUNt?')
        assert r == count, f'Failed on setting the average count ({count}). Received {r}'

        # def
        count = min(counts)
        self.inst.write(f'SENSe:AVERage:COUNt DEFault')
        r = self._get_int('SENSe:AVERage:COUNt?')
        assert r == count, f'Failed on setting the average count ({count}). Received {r}'

        # step
        step = 1

        # up
        count = min(counts)
        count_must_value = count + step
        self.inst.write(f'SENSe:AVERage:COUNt {count}')
        self.inst.write(f'SENSe:AVERage:COUNt UP')
        r = self._get_int('SENSe:AVERage:COUNt?')
        assert r == count_must_value, f'Failed on setting the average count ({count}). Received {r}'

        # down
        count = max(counts)
        count_must_value = count - step
        self.inst.write(f'SENSe:AVERage:COUNt {count}')
        self.inst.write(f'SENSe:AVERage:COUNt DOWN')
        r = self._get_int('SENSe:AVERage:COUNt?')
        assert r == count_must_value, f'Failed on setting the average count ({count}). Received {r}'

    def test_sens_period(self):
        periods = list(np.array(range(1, 100, 10)) * 1E-6)
        periods.append(100E-6)
        for period in periods:
            self.inst.write(f'SENSe:AVERage:PERiod {period} S')
            r = self._get_float('SENSe:AVERage:PERiod?')
            check_error_queue_and_assert(self.inst)
            assert abs(r - period) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} s'

        # min
        period = min(periods)
        self.inst.write(f'SENSe:AVERage:PERiod MINimum')
        r = self._get_float('SENSe:AVERage:PERiod?')
        assert abs(r - period) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} s'

        # max
        period = max(periods)
        self.inst.write(f'SENSe:AVERage:PERiod MAXimum')
        r = self._get_float('SENSe:AVERage:PERiod?')
        assert abs(r - period) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} s'

        # def
        period = 18E-6
        self.inst.write(f'SENSe:AVERage:PERiod DEFault')
        r = self._get_float('SENSe:AVERage:PERiod?')
        assert abs(r - period) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} s'

        # step
        step_s = 1E-6

        # up
        period = min(periods)
        period_must_value = period + step_s
        self.inst.write(f'SENSe:AVERage:PERiod {period} S')
        self.inst.write(f'SENSe:AVERage:PERiod UP')
        r = self._get_float('SENSe:AVERage:PERiod?')
        assert abs(r - period_must_value) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} s'

        # down
        period = periods[1]
        period_must_value = period - step_s
        self.inst.write(f'SENSe:AVERage:PERiod {period} S')
        self.inst.write(f'SENSe:AVERage:PERiod DOWN')
        r = self._get_float('SENSe:AVERage:PERiod?')
        rr = self.inst.query('SENSe:AVERage:PERiod?')
        assert abs(r - period_must_value) <= 10E-6, f'Failed on setting the period in averaging mode ({period}) s. Received {r} / {rr} s'

    def test_sens_period_random(self):
        periods = list(np.array(range(1, 11, 1)) * 1E-6)
        for period in periods:
            self.inst.write(f'SENSe:AVERage:PERiod:RANDom {period} S')
            r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
            check_error_queue_and_assert(self.inst)
            assert abs(r - period) <= 10E-6, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

        # min
        period = min(periods)
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom MINimum')
        r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
        assert abs(r - period) <= 10E-6, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

        # max
        period = max(periods)
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom MAXimum')
        r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
        assert abs(r - period) <= 10E-9, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

        # def
        period = 1e-6
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom DEFault')
        r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
        assert abs(r - period) <= 10E-6, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

        # step
        step_s = 10E-6

        # up
        period = min(periods)
        period_must_value = period + step_s
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom {period} S')
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom UP')
        r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
        assert abs(r - period_must_value) <= 10E-6, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

        # down
        period = periods[1]
        period_must_value = period - step_s
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom {period} S')
        self.inst.write(f'SENSe:AVERage:PERiod:RANDom DOWN')
        r = self._get_float('SENSe:AVERage:PERiod:RANDom?')
        assert abs(r - period_must_value) <= 10E-6, f'Failed on setting the random period in averaging mode ({period}) s. Received {r} s'

    def test_transmitter_mode(self):
        for mode_name in self.on_off_modes:
            self.inst.write(f'TRANsmitter:MODe {mode_name}')
            r = self.inst.query('TRANsmitter:MODe?')
            check_error_queue_and_assert(self.inst)
            assert r == mode_name, f'Failed on setting the transmitter mode ({mode_name}). Received {r} (0 id OFF, 1 is ON)'

    def test_transmitter_enable(self):
        for mode_name in self.on_off_modes:
            self.inst.write(f'TRANsmitter:ENABle {mode_name}')
            r = self.inst.query('TRANsmitter:ENABle?')
            check_error_queue_and_assert(self.inst)
            assert r == mode_name, f'Failed on setting the transmitter enable ({mode_name}). Received {r} (0 id OFF, 1 is ON)'

    def test_magnet_enable(self):
        for mode_name in self.on_off_modes:
            self.inst.write(f'MAGnet:ENABle {mode_name}')
            r = self.inst.query('MAGnet:ENABle?')
            check_error_queue_and_assert(self.inst)
            assert r == mode_name, f'Failed on setting the magnet enable ({mode_name}). Received {r} (0 id OFF, 1 is ON)'

    def test_magnet_voltage(self):
        voltages = range(15, 26, 1)
        for voltage in voltages:
            self.inst.write(f'MAGnet:VOLTage {voltage} V')
            r = int(self.inst.query('MAGnet:VOLTage?'))
            check_error_queue_and_assert(self.inst)
            assert r == voltage, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

        # min
        voltage = min(voltages)
        self.inst.write(f'MAGnet:VOLTage MINimum')
        r = int(self.inst.query('MAGnet:VOLTage?'))
        assert r == voltage, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

        # max
        voltage = max(voltages)
        self.inst.write(f'MAGnet:VOLTage MAXimum')
        r = int(self.inst.query('MAGnet:VOLTage?'))
        assert r == voltage, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

        # def
        voltage = 20
        self.inst.write(f'MAGnet:VOLTage DEFault')
        r = int(self.inst.query('MAGnet:VOLTage?'))
        assert r == voltage, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

        # step
        step = 1

        # up
        voltage = min(voltages)
        voltage_must_value = voltage + step
        self.inst.write(f'MAGnet:VOLTage {voltage} V')
        self.inst.write(f'MAGnet:VOLTage UP')
        r = int(self.inst.query('MAGnet:VOLTage?'))
        assert r == voltage_must_value, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

        # down
        voltage = voltages[1]
        voltage_must_value = voltage - step
        self.inst.write(f'MAGnet:VOLTage {voltage} V')
        self.inst.write(f'MAGnet:VOLTage DOWN')
        r = int(self.inst.query('MAGnet:VOLTage?'))
        assert r == voltage_must_value, f'Failed on setting the magnet voltage ({voltage}) V. Received {r} V'

    def test_magnet_delay(self):
        delays = list(np.array(range(10, 1310, 10)) * 1E-6)
        for delay in delays:
            self.inst.write(f'MAGnet:DELay {delay} S')
            r = float(self.inst.query('MAGnet:DELay?'))
            check_error_queue_and_assert(self.inst)
            assert abs(r - delay) <= 1E-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'
        
        # min
        delay = min(delays)
        self.inst.write(f'MAGnet:DELay MINimum')
        r = float(self.inst.query('MAGnet:DELay?'))
        assert abs(r - delay) <= 1E-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'

        # max
        delay = max(delays)
        self.inst.write(f'MAGnet:DELay MAXimum')
        r = float(self.inst.query('MAGnet:DELay?'))
        assert abs(r - delay) <= 1E-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'

        # def
        delay = 650E-6
        self.inst.write(f'MAGnet:DELay DEFault')
        r = float(self.inst.query('MAGnet:DELay?'))
        assert abs(r - delay) <= 1E-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'

        # step
        step = 1E-6

        # up
        delay = min(delays)
        delay_must_value = delay + step
        self.inst.write(f'MAGnet:DELay {delay} S')
        self.inst.write(f'MAGnet:DELay UP')
        r = float(self.inst.query('MAGnet:DELay?'))
        assert abs(r - delay_must_value) <= 1e-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'

        # down
        delay = delays[1]
        delay_must_value = delay - step
        self.inst.write(f'MAGnet:DELay {delay} S')
        self.inst.write(f'MAGnet:DELay DOWN')
        r = float(self.inst.query('MAGnet:DELay?'))
        assert abs(r - delay_must_value) <= 1e-6, f'Failed on setting the magnet delay ({delay}) s. Received {r} s'

