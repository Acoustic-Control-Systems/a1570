/**
 * A1570 WebSocket JavaScript Example
 * 
 * This example demonstrates how to connect to the A1570 device's WebSocket
 * for real-time data streaming (A-scan vectors, measurement results, etc.).
 * 
 * Usage in Browser:
 *   <script src="websocket_js_example.js"></script>
 * 
 * Usage in Node.js:
 *   npm install ws
 *   node websocket_js_example.js
 * 
 * Update the IP address below to match your device.
 */

// Device WebSocket URL
const DEVICE_IP = '192.168.0.1';
const WS_URL = `ws://${DEVICE_IP}/ws`;

// Create WebSocket connection
const ws = new WebSocket(WS_URL);

// Connection opened
ws.onopen = () => {
  console.log('WebSocket connection established');
  // You can send commands or subscribe to events here if needed
};

// Listen for messages
ws.onmessage = (event) => {
  try {
    // Try to parse as JSON first
    const data = JSON.parse(event.data);
    console.log('Received JSON:', data);
    // Handle measurement results, status updates, etc.
  } catch (e) {
    // If not JSON, it's likely binary data (A-scan vector)
    console.log('Received binary data:', event.data);
    // For binary data processing, you would typically convert to appropriate format
    // Example: const buffer = new Uint8Array(event.data);
  }
};

// Connection closed
ws.onclose = () => {
  console.log('WebSocket connection closed');
};

// Error handler
ws.onerror = (err) => {
  console.error('WebSocket error:', err);
};
