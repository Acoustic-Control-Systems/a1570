# A1570 REST API Examples

This directory contains code examples for interacting with the A1570 ultrasonic testing device via REST API and WebSocket.

## Files

### rest_api_python_examples.py

Complete Python example demonstrating the full workflow:

1. **Device Information Query** - Retrieves serial number and firmware version
2. **Configuration** - Sets acquisition parameters (GAIN, SAMPLING FREQ, ACCUMULATIONS, HV VOLTAGE)
3. **Start Measurement** - Initiates data acquisition
4. **WebSocket Data Reception** - Receives real-time A-scan data for 10 seconds
5. **Stop Measurement** - Stops acquisition
6. **Clean Disconnection** - Properly closes the WebSocket connection

**Dependencies:**
```bash
pip install requests websockets numpy
```

**Usage:**
```bash
python rest_api_python_examples.py
```

Update the `DEVICE_IP` variable at the top of the file to match your device's IP address.

**Key Features:**
- `A1570Device` class for REST API communication
- Error handling with timeouts
- Async WebSocket data reception
- Binary data parsing (Int16 arrays)
- Automatic connection management

### websocket_js_example.js

JavaScript WebSocket client example for browser or Node.js environments.

**Features:**
- WebSocket connection to device
- Event handlers for connection lifecycle
- Message parsing (JSON and binary)
- Error handling

**Usage in Browser:**
```html
<script src="websocket_js_example.js"></script>
```

**Usage in Node.js:**
```bash
npm install ws
node websocket_js_example.js
```

Update the IP address in the WebSocket URL to match your device.

## Quick Start

1. Ensure your A1570 device is connected to the network
2. Note the device's IP address (e.g., 192.168.0.1)
3. Update the `DEVICE_IP` or WebSocket URL in the example files
4. Install Python dependencies: `pip install requests websockets numpy`
5. Run the Python example: `python rest_api_python_examples.py`

## API Reference

For complete API documentation, see [REST-API.md](../REST-API.md).

## License

Copyright © ACS-Solutions GmbH 2025. All rights reserved.
