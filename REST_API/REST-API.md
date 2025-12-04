# A1570 REST API Documentation

## Overview

The A1570 ultrasonic testing device provides a comprehensive REST API for remote control and data acquisition. All API endpoints are accessible via HTTP POST requests with JSON payloads.

**Base URL:** `http://<device-ip>/api/`

**Content-Type:** All requests must include `Content-Type: application/json` header

**Response Format:** JSON

## API Endpoints

The device provides two main categories of endpoints:

1. **Standard Command Endpoints** (`/api/getValueCommand` and `/api/updateValueCommand`) - Used for most device parameters
2. **Exception Endpoints** (`/api/getValue` and `/api/updateValue`) - Used for specific device information parameters (serialNumber, version, firmwareVersion, dfuVersion, inputLoggingEnabled, doSendVectorWithResult)

### Standard Command Endpoints

Most device parameters use these endpoints with command IDs defined in the SCPI command set.

#### Query a Parameter Value

**Endpoint:** `/api/getValueCommand`

**Method:** POST

**Request Body:**
```json
{
  "id": "<COMMAND_ID>"
}
```

**Response:**
```json
{
  "id": "<COMMAND_ID>",
  "value": "<value>"
}
```

#### Update a Parameter Value

**Endpoint:** `/api/updateValueCommand`

**Method:** POST

**Request Body:**
```json
{
  "id": "<COMMAND_ID>",
  "value": "<value>"
}
```

**Response:**
```json
{
  "id": "<COMMAND_ID>",
  "value": "<value>"
}
```

### Exception Endpoints

The following parameters use `/api/getValue` and `/api/updateValue` instead of the command endpoints:
- `serialNumber` (read-only)
- `version` (read-only)
- `firmwareVersion` (read-only)
- `dfuVersion` (read-only)
- `inputLoggingEnabled`
- `doSendVectorWithResult`

## Available Commands

### Acquisition Control

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| START AUTO ASCAN | - | Start acquisition |
| STOP AUTO ASCAN | - | Stop acquisition |
| MEASUREMENT PRR | 1-4 | Periodic acquisition interval |

### Input Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| GAIN | 0-40 dB | Constant gain at input |
| SOURCE SYNC TYPE | INTERNAL \| EXTERNAL | Acquisition triggering mode |
| SAMPLING FREQ | 25 \| 50 \| 100 MHz | Input sampling rate |
| ACCUMULATIONS | 0-4 | Acquisitions per averaged vector |
| FILTER | integer | Digital high-pass filter number |

### Transmitter Settings

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| HV VOLTAGE | 200 \| 400 \| 600 V | Transmitter pulse amplitude |
| ZONDER FREQUENCY | 20-20000 kHz | Transmitter burst frequency |
| ZONDER PERIODS | 0.5-8.0 periods | Transmitter burst duration |
| ZONDER ENABLE | ON \| OFF | Transmitter enable |
| ZONDER REVERSE POLARITY | ON \| OFF | Transducer polarity mode |

### Magnet Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| MAGNET ENABLE | ON \| OFF | Magnet enabled |
| MAGNET VOLTAGE | 15-25 V | Magnet voltage |
| MAGNET DELAY | 10-1300 µs | Magnet delay |

### Measurement Commands

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| RESULT MEASURE | read-only | Thickness measurement status/result |
| START MEASURE | - | Start automatic thickness measurement |
| START STROBE PEAK | - | Start single peak measurement in strobe |
| START STROBE P2P | - | Start peak-to-peak distance measurement |

### Calibration Commands

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| START CAL AIR | - | Start calibration in air |
| START CAL OBJ | - | Start calibration on object surface |

### Probe Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| PROBE TYPE | S3950, S7692, S7694, S7394, S7392 | Probe type identifier |
| SOUND VELOCITY | 1000-10000 m/s | Sound velocity in material |
| PROBE DELAY PROCESSING | 0-100 µs | Probe delay compensation |
| PROBE TEMPERATURE | °C (read-only) | Temperature of pulse magnet probe |

### Device Status

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| BATTERY | 0-100% (read-only) | Battery charge level |
| CHARGE STATUS | read-only | Charger connection status |

### Processing Parameters

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| DEAD ZONES | string | Dead zone configuration |
| NOISE PARAMETERS | string | Noise parameters for pulse magnet probes |
| EDDY CALIBRATION ARRAY | string | Eddy current calibration data |
| SOFTWARE AVERAGING COUNT | 0-100 | Software averaging count |

### Gate (Strobe) Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| ASCAN STROBE BEGIN | 0-8192 | Gate start position (samples) |
| ASCAN STROBE WIDTH | 0-8192 | Gate width (samples) |
| ASCAN STROBE LEVEL | 0-100 | Gate threshold level (% of maximum signal amplitude) |

## Error Responses

All endpoints return standard HTTP status codes:

- **200 OK** - Request successful
- **400 Bad Request** - Invalid parameters, missing required fields, or malformed JSON
- **500 Internal Server Error** - Server-side processing error (e.g., queue full, failed to add request)

Error responses include a descriptive text message.

## Usage Examples

### curl Examples

#### Query Parameter Value

```bash
curl -X POST http://192.168.1.100/api/getValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'GAIN'}"
```

Response:
```json
{"id":"GAIN","value":"20"}
```

#### Update Parameter Value

```bash
curl -X POST http://192.168.1.100/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'GAIN','value':'30'}"
```

Response:
```json
{"id":"GAIN","value":"30"}
```

#### Start Acquisition

```bash
curl -X POST http://192.168.1.100/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'START AUTO ASCAN'}"
```

#### Set Sampling Frequency

```bash
curl -X POST http://192.168.1.100/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'SAMPLING FREQ','value':'100'}"
```

#### Query Device Information (Exception Endpoint)

```bash
curl -X POST http://192.168.1.100/api/getValue \
    -H "Content-Type: application/json" \
    -d "{'id':'serialNumber'}"
```

Response:
```json
{"id":"serialNumber","value":"A1570-12345"}
```

### Python Examples

Install the requests library:
```bash
pip install requests
```

#### Basic Parameter Query and Update

```python
import requests
import json

# Device configuration
DEVICE_IP = "192.168.1.100"
BASE_URL = f"http://{DEVICE_IP}/api"

def get_parameter(command_id):
    """Query a parameter value using /api/getValueCommand"""
    url = f"{BASE_URL}/getValueCommand"
    payload = {"id": command_id}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("value")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def set_parameter(command_id, value):
    """Update a parameter value using /api/updateValueCommand"""
    url = f"{BASE_URL}/updateValueCommand"
    payload = {"id": command_id, "value": str(value)}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("value")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Example usage
current_gain = get_parameter("GAIN")
print(f"Current GAIN: {current_gain} dB")

new_gain = set_parameter("GAIN", 25)
print(f"New GAIN: {new_gain} dB")
```

#### Start and Stop Acquisition

```python
import requests
import time

DEVICE_IP = "192.168.1.100"
BASE_URL = f"http://{DEVICE_IP}/api"

def send_command(command_id, value=None):
    """Send a command to the device"""
    url = f"{BASE_URL}/updateValueCommand"
    payload = {"id": command_id}
    if value is not None:
        payload["value"] = str(value)
    
    response = requests.post(url, json=payload)
    return response.status_code == 200

# Configure acquisition parameters
send_command("GAIN", 30)
send_command("SAMPLING FREQ", 100)  # 100 MHz
send_command("ACCUMULATIONS", 2)

# Start acquisition
print("Starting acquisition...")
send_command("START AUTO ASCAN")

# Run for 10 seconds
time.sleep(10)

# Stop acquisition
print("Stopping acquisition...")
send_command("STOP AUTO ASCAN")
```

#### Query Device Information (Exception Endpoints)

```python
import requests

DEVICE_IP = "192.168.1.100"
BASE_URL = f"http://{DEVICE_IP}/api"

def get_exception_parameter(param_id):
    """Query exception endpoint parameters using /api/getValue"""
    url = f"{BASE_URL}/getValue"
    payload = {"id": param_id}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("value")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Query device information
serial = get_exception_parameter("serialNumber")
version = get_exception_parameter("version")
fw_version = get_exception_parameter("firmwareVersion")

print(f"Serial Number: {serial}")
print(f"Version: {version}")
print(f"Firmware Version: {fw_version}")
```

#### Error Handling with Timeout

```python
import requests
from requests.exceptions import Timeout, RequestException

DEVICE_IP = "192.168.1.100"
BASE_URL = f"http://{DEVICE_IP}/api"
TIMEOUT = 5  # seconds

def set_parameter_safe(command_id, value):
    """Update a parameter with error handling and timeout"""
    url = f"{BASE_URL}/updateValueCommand"
    payload = {"id": command_id, "value": str(value)}
    
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {command_id} set to {data.get('value')}")
            return True
        elif response.status_code == 400:
            print(f"Bad request: {response.text}")
            return False
        elif response.status_code == 500:
            print(f"Server error: {response.text}")
            return False
        else:
            print(f"Unexpected status {response.status_code}: {response.text}")
            return False
            
    except Timeout:
        print(f"Request timeout after {TIMEOUT} seconds")
        return False
    except RequestException as e:
        print(f"Request failed: {e}")
        return False

# Example usage
set_parameter_safe("GAIN", 35)
set_parameter_safe("HV VOLTAGE", 400)
```

#### Complete Device Configuration Example

```python
import requests
import time

DEVICE_IP = "192.168.1.100"
BASE_URL = f"http://{DEVICE_IP}/api"

class A1570Device:
    def __init__(self, ip_address):
        self.base_url = f"http://{ip_address}/api"
        self.timeout = 5
    
    def get_parameter(self, command_id):
        """Query a parameter value"""
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
        """Update a parameter value"""
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
        """Query device information using exception endpoint"""
        url = f"{self.base_url}/getValue"
        payload = {"id": param_id}
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("value")
        except Exception as e:
            print(f"Error querying {param_id}: {e}")
        return None
    
    def configure_acquisition(self, gain=30, sampling_freq=100, 
                             accumulations=2, hv_voltage=400):
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

# Example usage
device = A1570Device("192.168.1.100")

# Get device information
print("=== Device Information ===")
print(f"Serial Number: {device.get_device_info('serialNumber')}")
print(f"Firmware Version: {device.get_device_info('firmwareVersion')}")
print()

# Configure acquisition
print("=== Configuring Acquisition ===")
if device.configure_acquisition(gain=30, sampling_freq=100, 
                               accumulations=2, hv_voltage=400):
    print("Configuration successful")
    
    # Verify settings
    print(f"GAIN: {device.get_parameter('GAIN')} dB")
    print(f"SAMPLING FREQ: {device.get_parameter('SAMPLING FREQ')} MHz")
    print()
    
    # Start acquisition
    print("Starting acquisition...")
    device.start_acquisition()
    
    # Run for 10 seconds
    time.sleep(10)
    
    # Stop acquisition
    print("Stopping acquisition...")
    device.stop_acquisition()
    print("Done")
else:
    print("Configuration failed")
```

## WebSocket Integration

The A1570 device supports real-time data streaming and event notifications via WebSocket. This is primarily used for high-throughput transfer of A-scan vectors, measurement results, and device status updates.

### How to Use WebSockets

- **Endpoint:**
  - Connect to `ws://<device-ip>/ws` (replace `<device-ip>` with your device's IP address)

- **Connection Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://192.168.1.100/ws');
ws.onopen = () => {
  console.log('WebSocket connection established');
  // You can send commands or subscribe to events here
};
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  // Handle measurement results, status updates, etc.
};
ws.onclose = () => {
  console.log('WebSocket connection closed');
};
ws.onerror = (err) => {
  console.error('WebSocket error:', err);
};
```

- **Typical Workflow:**
  1. Establish a WebSocket connection after device configuration (using REST API)
  2. Listen for incoming messages containing measurement data
  
## Network Configuration

The device provides additional REST API endpoints for network configuration, firmware updates, preset management, and logging. See the complete API documentation in the device manual for details on these specialized endpoints.

## Notes

- All numeric values should be sent as strings in JSON payloads
- Command IDs are case-sensitive
- Some parameters are read-only (check Argument/Range column)
- The device uses internal command translation from web interface IDs to SCPI command IDs
- Response times vary depending on device processing load; implement appropriate timeouts
- For parameters with enumerated values (e.g., `SAMPLING FREQ`), use the exact value strings as specified

## License

Copyright © ACS-Solutions GmbH 2025. All rights reserved.
