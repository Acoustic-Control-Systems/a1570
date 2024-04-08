def check_error_queue_and_assert(inst):
    msg_num, msg_str = read_error_queue(inst)
    assert msg_num == 0, f'Found error in queue: {msg_str}'

def check_error_queue_and_assert_if_no_error(inst):
    msg_num, msg_str = read_error_queue(inst)
    assert msg_num != 0, f'No error in queue found: {msg_str}'

def read_error_queue(inst):
    error = inst.query(f'SYSTem:ERRor?')
    msg_num, msg_str = parse_error(error)
    return msg_num, msg_str

def read_error_queue(inst):
    error = inst.query(f'SYSTem:ERRor?')
    msg_num, msg_str = parse_error(error)
    return msg_num, msg_str

def parse_error(error_msg: str):
    msg_spl = error_msg.split(',', 1)
    num = int(msg_spl[0])
    msg = msg_spl[1] if len(msg_spl) == 2 else ''
    return num, msg

# parse string of format "0:10;5:11;10:12;15:13;20:14;25:15;30:16;35:17;40:18" into list of tuples 'gain:dead_zone'
def parse_dead_zones(answ)->list[tuple[int, int]]:
    # parse string of format "0:10;5:11;10:12;15:13;20:14;25:15;30:16;35:17;40:18" into list of tuples
    dead_zones = [tuple(map(int, dz.split(':'))) for dz in answ.split(';')]
    return dead_zones

def parse_measurement_result(answ):
    # parse json of result of format:
    # {
    #     "command": "measurement_result",
    #     "contact": false,
    #     "contact_quality": 0,
    #     "counter" : 0, 
    #     "gain": 0,
    #     "thickness": 65535,
    #     "timestamp" : "12:10:49"
    # }
    import json
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
    class Result:
        def __init__(self, command, contact, contact_quality, counter, gain, thickness, timestamp):
            self.command = command
            self.contact = contact
            self.contact_quality = contact_quality
            self.counter = counter
            self.gain = gain
            self.thickness = thickness # in mm
            self.timestamp = timestamp

    result_obj = Result(command, contact, contact_quality, counter, gain, thickness, timestamp)

    return result_obj