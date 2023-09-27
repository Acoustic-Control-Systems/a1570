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