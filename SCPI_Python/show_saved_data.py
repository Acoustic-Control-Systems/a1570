from dataclasses import dataclass
import os
import struct
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
import logging

# Define a data class for block parameters
@dataclass
class BlockParameters:
    gain: int # dB
    pulse_level: int # V
    sampling_rate: int # MHz
    duration: float # number of periods 0.5, 1 ... 8
    averaging: int = 4 # 2^averaging
    probe_frequency: float = 3 # MHz


def load_from_json_file(filename:str):#->tuple[BlockParameters, b]:
    import json
    with open(filename, 'r') as f:
        data = json.load(f)
        parameters = BlockParameters(**data['parameters'])
        return parameters, data['data']

directory = 'data_blocks'

#sort files by date descending
files = sorted(os.listdir(directory), key=lambda x: os.path.getmtime(f'{directory}/{x}'), reverse=True)

fig = plt.figure()
# , load all files from the directory
for filename in files:
    if filename.endswith(".json"):
        print(f'Loading {filename}...')
        params, data = load_from_json_file(f'{directory}/{filename}')
        print(params)
        #plot data on new figure
        fig.clear()
        plt.plot(data)
        plt.title(f'{filename}')
        # pause 1 second
        plt.pause(0.1)
    
        
        

