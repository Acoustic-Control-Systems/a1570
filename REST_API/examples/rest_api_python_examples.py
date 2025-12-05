"""
A1570 REST API Python Example

This example demonstrates:
1. Querying device information
2. Configuring acquisition parameters
3. Starting measurement
4. Receiving real-time data via WebSocket
5. Stopping measurement and disconnecting

Dependencies:
    pip install requests websockets numpy

Usage:
    Update DEVICE_IP and run: python rest_api_python_examples.py
"""

import asyncio
import time
import requests
import websockets
import numpy as np
from requests.exceptions import Timeout, RequestException

# Device configuration
DEVICE_IP = "192.168.0.2"
BASE_URL = f"http://{DEVICE_IP}/api"
WS_URL = f"ws://{DEVICE_IP}/ws"
TIMEOUT = 5  # seconds


class A1570Device:
    """A1570 device REST API client"""
    
    def __init__(self, ip_address, timeout=5):
        self.base_url = f"http://{ip_address}/api"
        self.timeout = timeout
    
    def get_parameter(self, command_id):
        """Query a parameter value using /api/getValueCommand"""
        url = f"{self.base_url}/getValueCommand"
        payload = {"id": command_id}
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("value")
        except Exception as e:
            print(f"Error querying {command_id}: {e}")
        return None
    
    def set_parameter(self, command_id, value):
        """Update a parameter value using /api/updateValueCommand"""
        url = f"{self.base_url}/updateValueCommand"
        payload = {"id": command_id, "value": str(value)}
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                return True
        except Exception as e:
            print(f"Error setting {command_id}: {e}")
        return False
    
    def send_command(self, command_id):
        """Send a command without value"""
        return self.set_parameter(command_id, "")
    
    def get_device_info(self, param_id):
        """Query device information using exception endpoint /api/getValue"""
        url = f"{self.base_url}/getValue"
        payload = {"id": param_id}
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("value")
        except Exception as e:
            print(f"Error querying {param_id}: {e}")
        return None
    
    def configure_acquisition(self, gain=30, sampling_freq=100, accumulations=2, hv_voltage=400):
        """Configure acquisition parameters"""
        params = {
            "GAIN": gain,
            "SAMPLING FREQ": sampling_freq,
            "ACCUMULATIONS": accumulations,
            "HV VOLTAGE": hv_voltage
        }
        for cmd, val in params.items():
            if not self.set_parameter(cmd, val):
                print(f"Failed to set {cmd}")
                return False
        return True
    
    def start_acquisition(self):
        """Start data acquisition"""
        return self.send_command("START AUTO ASCAN")
    
    def stop_acquisition(self):
        """Stop data acquisition"""
        return self.send_command("STOP AUTO ASCAN")


def main():
    """Main workflow: configure, measure, receive data, stop"""
    device = A1570Device(DEVICE_IP)
    
    # Query device information
    print("=== Device Information ===")
    print(f"Serial Number: {device.get_device_info('serialNumber')}")
    print(f"Device Version Full: {device.get_device_info('version')}")
    print()
    
    # Configure acquisition
    print("=== Configuring Acquisition ===")
    if not device.configure_acquisition(gain=30, sampling_freq=100, accumulations=2, hv_voltage=400):
        print("Configuration failed")
        return
    
    print("Configuration successful")
    print(f"GAIN: {device.get_parameter('GAIN')} dB")
    print(f"SAMPLING FREQ: {device.get_parameter('SAMPLING FREQ')} MHz")
    print()
    
    # Start acquisition
    print("Starting acquisition...")
    device.start_acquisition()
    
    # Receive WebSocket data for 10 seconds
    async def run_websocket():
        try:
            async with websockets.connect(WS_URL) as ws:
                print("WebSocket connection established.")
                start_time = time.time()
                while time.time() - start_time < 10:
                    data = await ws.recv()
                    if isinstance(data, (bytes, bytearray)):
                        arr = np.frombuffer(data, dtype=np.int16)
                        print(f"Received {len(arr)} samples. First value: {arr[0]}")
                    else:
                        print("Received text message:", data)
                print("WebSocket connection closed.")
        except Exception as e:
            print(f"WebSocket error: {e}")
    
    asyncio.run(run_websocket())
    
    # Stop acquisition
    print("Stopping acquisition...")
    device.stop_acquisition()
    print("Done")


if __name__ == "__main__":
    main()
