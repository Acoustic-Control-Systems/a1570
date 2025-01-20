"""
Common utility functions for working with A1570 EMAT device via SCPI.

This module provides helper functions for:
- Error queue handling and parsing
- Dead zone parameter parsing
- Measurement result parsing from JSON
"""

import json
from typing import Tuple, List

def check_error_queue_and_assert(inst) -> None:
    """Assert that error queue is empty.
    
    Args:
        inst: VISA instrument instance
        
    Raises:
        AssertionError: If error found in queue
    """
    msg_num, msg_str = read_error_queue(inst)
    assert msg_num == 0, f'Found error in queue: {msg_str}'

def check_error_queue_and_assert_if_no_error(inst) -> None:
    """Assert that error queue contains an error.
    
    Args:
        inst: VISA instrument instance
        
    Raises:
        AssertionError: If no error found in queue
    """
    msg_num, msg_str = read_error_queue(inst) 
    assert msg_num != 0, f'No error in queue found: {msg_str}'

def read_error_queue(inst) -> Tuple[int, str]:
    """Read and parse error from device error queue.
    
    Args:
        inst: VISA instrument instance
        
    Returns:
        Tuple[int, str]: Error number and message
    """
    error = inst.query(f'SYSTem:ERRor?')
    msg_num, msg_str = parse_error(error)
    return msg_num, msg_str

def parse_error(error_msg: str) -> Tuple[int, str]:
    """Parse error message string into number and description.
    
    Args:
        error_msg: Raw error message string from device
        
    Returns:
        Tuple[int, str]: Error number and message text
    """
    msg_spl = error_msg.split(',', 1)
    num = int(msg_spl[0])
    msg = msg_spl[1] if len(msg_spl) == 2 else ''
    return num, msg

def parse_dead_zones(answ: str) -> List[Tuple[int, int]]:
    """Parse dead zone string into list of gain/zone tuples.
    
    Args:
        answ: String like "0:10;5:11;10:12" with gain:zone pairs
        
    Returns:
        List[Tuple[int, int]]: List of (gain, dead_zone) pairs
        
    Example:
        >>> parse_dead_zones("0:10;5:11")
        [(0, 10), (5, 11)]
    """
    dead_zones = [tuple(map(int, dz.split(':'))) for dz in answ.split(';')]
    return dead_zones

class Result:
    def __init__(self, command, contact, contact_quality, counter, gain, thickness, timestamp):
        self.command = command
        self.contact = contact
        self.contact_quality = contact_quality
        self.counter = counter
        self.gain = gain
        self.thickness = thickness # in mm
        self.timestamp = timestamp

def parse_measurement_result(answ: str) -> Result:
    """Parse JSON measurement result into Result object.
    
    {
        "command": "measurement_result",
        "contact": false,
        "contact_quality": 0,
        "counter" : 0, 
        "gain": 0,
        "thickness": 65535,
        "timestamp" : "12:10:49"
    }

    Args:
        answ: JSON string containing measurement data
        
    Returns:
        Result: Object containing parsed measurement values
    """
    result = json.loads(answ)
    command = result['command']
    contact = result['contact']
    contact_quality = result['contact_quality']
    counter = result['counter']
    gain = result['gain']
    thickness = result['thickness']
    # convert thickness from um to mm
    thickness = thickness / 1000
    timestamp = result['timestamp']
    
    # create an object
    result_obj = Result(command, contact, contact_quality, counter, gain, thickness, timestamp)

    return result_obj