"""
Simplified BCI backend simulator
"""
import json
import time
import random
import threading
import os
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from urllib.parse import parse_qs

# Global state
device_connected = False
is_generating_data = False
generation_thread = None
mock_data = {
    "eeg_data": {
        "channels": [0, 0, 0, 0],
        "timestamp": 0,
        "labels": ["Alpha", "Beta", "Theta", "Delta"]
    },
    "mental_state": {
        "state": "neutral",
        "confidence": 0.5,
        "left_brain_activity": 0.5,
        "right_brain_activity": 0.5,
        "blink_detected": False,
        "timestamp": 0
    }
}

# Simulates different mental states based on sin waves
def get_oscillating_value(speed=0.1, min_val=0.2, max_val=0.8):
    """Get a value that oscillates between min and max"""
    return min_val + (max_val - min_val) * (math.sin(time.time() * speed) * 0.5 + 0.5)

def data_generation_loop():
    """Generate fake brain and eye data"""
    global mock_data, is_generating_data
    
    while is_generating_data:
        # Generate oscillating values for left and right brain
        time_base = time.time()
        left_activity = get_oscillating_value(speed=0.2, min_val=0.3, max_val=0.9)
        right_activity = get_oscillating_value(speed=0.15, min_val=0.3, max_val=0.9)
        
        # Determine if this should be a blink moment
        blink_detected = random.random() < 0.05  # 5% chance of blink
        
        # Generate brain state
        if left_activity > right_activity + 0.2:
            state = "analytical"
        elif right_activity > left_activity + 0.2:
            state = "creative"
        else:
            state = "balanced"
            
        # Generate fake EEG data
        alpha = 5 + 10 * left_activity + random.uniform(-1, 1)
        beta = 5 + 10 * right_activity + random.uniform(-1, 1)
        theta = 5 + 5 * (left_activity + right_activity) / 2 + random.uniform(-1, 1)
        delta = 3 + 2 * (1 - (left_activity + right_activity) / 2) + random.uniform(-0.5, 0.5)
        
        # Update the mock data
        mock_data = {
            "eeg_data": {
                "channels": [alpha, beta, theta, delta],
                "timestamp": time_base,
                "labels": ["Alpha", "Beta", "Theta", "Delta"]
            },
            "mental_state": {
                "state": state,
                "confidence": 0.7 + random.uniform(-0.1, 0.1),
                "left_brain_activity": left_activity,
                "right_brain_activity": right_activity,
                "blink_detected": blink_detected,
                "timestamp": time_base
            }
        }
        
        # Sleep to simulate realistic data rates
        time.sleep(0.1)  # 10Hz update rate

class BCIRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json_response(self, data):
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests for CORS
        self._set_headers()
        self.wfile.write(b'')
    
    def do_GET(self):
        global device_connected, mock_data
        
        # Parse the path to route the request
        path = self.path.split('?')[0]
        
        if path == '/api/status':
            self._set_headers()
            self._send_json_response({
                "status": "ok",
                "version": "1.0.0",
                "device_connected": device_connected
            })
        
        elif path == '/api/eeg':
            self._set_headers()
            if not device_connected:
                self._send_json_response({"success": False, "error": "Device not connected"})
            else:
                self._send_json_response({"success": True, "data": mock_data["eeg_data"]})
        
        elif path == '/api/mental_state':
            self._set_headers()
            if not device_connected:
                self._send_json_response({"success": False, "error": "Device not connected"})
            else:
                self._send_json_response({"success": True, "data": mock_data["mental_state"]})
        
        elif path == '/api/dataset_status':
            self._set_headers()
            self._send_json_response({
                "success": True,
                "hasDataset": True
            })
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        global device_connected, is_generating_data, generation_thread
        
        content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            if content_length > 0:
                request_data = json.loads(post_data)
            else:
                request_data = {}
        except:
            request_data = {}
        
        if self.path == '/api/connect':
            if device_connected:
                self._set_headers()
                self._send_json_response({"success": False, "error": "already_connected"})
                return
            
            use_webcam = request_data.get('use_webcam', False)
            device_connected = True
            is_generating_data = True
            
            # Start data generation thread
            generation_thread = threading.Thread(target=data_generation_loop)
            generation_thread.daemon = True
            generation_thread.start()
            
            self._set_headers()
            self._send_json_response({
                "success": True,
                "message": f"Connected successfully using {'webcam' if use_webcam else 'simulation'} mode"
            })
        
        elif self.path == '/api/disconnect':
            device_connected = False
            is_generating_data = False
            
            # Allow thread to terminate naturally
            if generation_thread and generation_thread.is_alive():
                time.sleep(0.5)
            
            self._set_headers()
            self._send_json_response({"success": True, "message": "Disconnected successfully"})
        
        elif self.path == '/api/bypass':
            device_connected = False
            is_generating_data = False
            
            self._set_headers()
            self._send_json_response({"success": True, "message": "Connection state reset successfully"})
        
        elif self.path == '/api/start_mock':
            if is_generating_data:
                self._set_headers()
                self._send_json_response({"success": False, "error": "Already generating data"})
                return
            
            is_generating_data = True
            generation_thread = threading.Thread(target=data_generation_loop)
            generation_thread.daemon = True
            generation_thread.start()
            
            self._set_headers()
            self._send_json_response({"success": True, "message": "Mock data generation started"})
        
        elif self.path == '/api/stop_mock':
            is_generating_data = False
            
            self._set_headers()
            self._send_json_response({"success": True, "message": "Mock data generation stopped"})
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, BCIRequestHandler)
    print(f"Starting BCI Interface backend on port {port}...")
    print("Press Ctrl+C to quit")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped")

if __name__ == '__main__':
    run_server()