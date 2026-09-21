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
- `serialNumber` (read-only) : Serial number of A1570 device.
- `version` (read-only) : Full version info of A1570 device.
- `doSendVectorWithResult` : Enable sending raw data together with measurement result.

## Available Commands

### Acquisition Control

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| START AUTO ASCAN | - | Start acquisition |
| STOP AUTO ASCAN | - | Stop acquisition |
| MEASUREMENT PRR | 1-4 | Periodic acquisition interval (Hz) |

### Input Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| GAIN | 0-40 | Constant gain at input (dB) |
| SOURCE SYNC TYPE | INTERNAL \| EXTERNAL | Acquisition triggering mode |
| SAMPLING FREQ | 25 \| 50 \| 100 | Input sampling rate (MHz) |
| ACCUMULATIONS | 0-4 | Acquisitions per averaged vector |
| FILTER | integer | Digital high-pass filter number |

### Transmitter Settings

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| HV VOLTAGE | 200 \| 400 \| 600 | Transmitter pulse amplitude (V) |
| ZONDER FREQUENCY | 20-20000 | Transmitter burst frequency (kHz) |
| ZONDER PERIODS | 0.5-8.0 | Transmitter burst duration (periods) |
| ZONDER ENABLE | ON \| OFF | Transmitter enable |
| ZONDER REVERSE POLARITY | ON \| OFF | Transducer polarity mode |

### Magnet Configuration

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| MAGNET ENABLE | ON \| OFF | Magnet enabled |
| MAGNET VOLTAGE | 15-25 | Magnet voltage (V) |
| MAGNET DELAY | 10-1300 | Magnet delay (µs) |

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
| SOUND VELOCITY | 1000-10000 | Sound velocity in material (m/s) |
| PROBE DELAY PROCESSING | 0-100 | Probe delay compensation (µs) |
| PROBE TEMPERATURE | read-only | Temperature of pulse magnet probe (°C) |

### Device Status

| Command ID | Argument/Range | Description |
|------------|----------------|-------------|
| BATTERY | 0-100 | Battery charge level (%) |
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

#### Query a parameter:
```bash
curl -X POST http://192.168.0.1/api/getValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'GAIN'}"
```

Response:
```json
{"id":"GAIN","value":"20"}
```

#### Update a parameter

```bash
curl -X POST http://192.168.0.1/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'GAIN','value':'30'}"
```

Response:
```json
{"id":"GAIN","value":"30"}
```

#### Start Acquisition

```bash
curl -X POST http://192.168.0.1/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'START AUTO ASCAN'}"
```

#### Set Sampling Frequency

```bash
curl -X POST http://192.168.0.1/api/updateValueCommand \
    -H "Content-Type: application/json" \
    -d "{'id':'SAMPLING FREQ','value':'100'}"
```

#### Query Device Information (Exception Endpoint)

```bash
curl -X POST http://192.168.0.1/api/getValue \
    -H "Content-Type: application/json" \
    -d "{'id':'serialNumber'}"
```
Response:
```json
{"id":"serialNumber","value":"A1570-12345"}
```
## WebSocket Integration

The A1570 device supports real-time data streaming and event notifications via WebSocket. This is primarily used for high-throughput transfer of A-scan vectors, measurement results, and device status updates.

**Endpoint:** `ws://<device-ip>/ws`

**Typical Workflow:**
1. Configure device using REST API
2. Start acquisition using REST API
3. Establish WebSocket connection
4. Receive measurement data streams
5. Stop acquisition and disconnect

### Examples

Complete working examples are available in the `examples/` directory:

- **[examples/rest_api_python_examples.py](examples/rest_api_python_examples.py)** - Full Python workflow with REST API and WebSocket
- **[examples/websocket_js_example.js](examples/websocket_js_example.js)** - JavaScript WebSocket client

See **[examples/README.md](examples/README.md)** for detailed documentation and usage instructions.


## Network Configuration

The device provides additional REST API endpoints for network configuration, firmware updates, preset management, and logging. See the complete API documentation in the device manual for details on these specialized endpoints.

## Notes

- All numeric values should be sent as strings in JSON payloads
- Command IDs are case-sensitive
- Some parameters are read-only (check Argument/Range column)
- Response times vary depending on device processing load; implement appropriate timeouts
- For parameters with enumerated values (e.g., `SAMPLING FREQ`), use the exact value strings as specified
- Device documentation could be found [here](https://subscribe.acs-international.online/product/download/17)

## License

Copyright © ACS-Solutions GmbH 2025. All rights reserved.
