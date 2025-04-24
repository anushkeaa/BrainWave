"""
BCI backend server that uses real CSV data for analysis
"""
import json
import time
import random
import threading
import math
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# Try to import our CSV processors
try:
    from csv_processor import BrainActivityAnalyzer
    # Try to import the specialized adapters
    try:
        from mental_state_adapter import MentalStateAdapter
        print("Successfully imported Mental State adapter")
        MENTAL_STATE_ADAPTER_AVAILABLE = True
    except ImportError:
        print("Mental State adapter not available.")
        MENTAL_STATE_ADAPTER_AVAILABLE = False
        
    # Try to import the eye gaze adapters
    try:
        from eyegaze_adapter import EyeGazeAdapter
        print("Successfully imported Eye Gaze adapter")
        EYEGAZE_ADAPTER_AVAILABLE = True
    except ImportError:
        print("Eye Gaze adapter not available.")
        EYEGAZE_ADAPTER_AVAILABLE = False
        
    # Try to import the custom eye gaze adapter
    try:
        from custom_eyegaze_adapter import CustomEyeGazeAdapter
        print("Successfully imported Custom Eye Gaze adapter")
        CUSTOM_EYEGAZE_ADAPTER_AVAILABLE = True
    except ImportError:
        print("Custom Eye Gaze adapter not available.")
        CUSTOM_EYEGAZE_ADAPTER_AVAILABLE = False
        
    print("Successfully imported CSV processor")
    USE_REAL_DATA = True
except ImportError:
    print("WARNING: Could not import CSV processor. Using simulated data.")
    USE_REAL_DATA = False
    MENTAL_STATE_ADAPTER_AVAILABLE = False
    EYEGAZE_ADAPTER_AVAILABLE = False
    CUSTOM_EYEGAZE_ADAPTER_AVAILABLE = False

# Global state
device_connected = False
is_generating_data = False
generation_thread = None
using_webcam = False

# Initialize brain data with default values
brain_data = {
    "left": 0.5,
    "right": 0.5,
    "state": "neutral",
    "eye_position": "center",
    "blink": False,
    "timestamp": time.time()
}

# Try to initialize the brain activity analyzer
try:
    if USE_REAL_DATA:
        # Check for specialized datasets
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        mental_state_path = os.path.join(data_dir, "mental-state.csv")
        
        # Look for eyegaze dataset first
        eyegaze_found = False
        eyegaze_path = None
        eyegaze_analyzer = None
        
        # Try custom adapter first with your specific format
        if CUSTOM_EYEGAZE_ADAPTER_AVAILABLE:
            for filename in ["eyegaze.csv", "eye_gaze.csv", "eye-gaze.csv", "eyetracking.csv"]:
                potential_path = os.path.join(data_dir, filename)
                if os.path.exists(potential_path):
                    eyegaze_path = potential_path
                    print(f"Found eyegaze dataset: {eyegaze_path}")
                    print("Trying custom eyegaze adapter for your specific format...")
                    eyegaze_analyzer = CustomEyeGazeAdapter(eyegaze_path)
                    if hasattr(eyegaze_analyzer, 'using_simulated_data') and not eyegaze_analyzer.using_simulated_data:
                        print("Successfully initialized custom eyegaze analyzer!")
                        eyegaze_found = True
                        break
                    else:
                        print("Custom adapter did not recognize the dataset format, trying standard adapter...")
        
        # If custom adapter didn't work, try standard adapter
        if not eyegaze_found and EYEGAZE_ADAPTER_AVAILABLE:
            for filename in ["eyegaze.csv", "eye_gaze.csv", "eye-gaze.csv", "eyetracking.csv"]:
                potential_path = os.path.join(data_dir, filename)
                if os.path.exists(potential_path):
                    eyegaze_path = potential_path
                    eyegaze_analyzer = EyeGazeAdapter(eyegaze_path)
                    if hasattr(eyegaze_analyzer, 'using_simulated_data') and not eyegaze_analyzer.using_simulated_data:
                        print("Successfully initialized standard eyegaze analyzer with real data")
                        eyegaze_found = True
                        break
                    else:
                        print("Standard eyegaze adapter is using simulated data internally")
        
        # Check for mental-state.csv
        if MENTAL_STATE_ADAPTER_AVAILABLE and os.path.exists(mental_state_path):
            # Use the mental state adapter
            print(f"Using mental-state.csv dataset: {mental_state_path}")
            brain_analyzer = MentalStateAdapter(mental_state_path)
            if hasattr(brain_analyzer, 'using_simulated_data') and brain_analyzer.using_simulated_data:
                print("Mental State adapter is using simulated data internally")
        else:
            # Use the default analyzer with any available CSV
            brain_analyzer = BrainActivityAnalyzer()
            
            # Check if it's using simulated data internally
            if hasattr(brain_analyzer, 'using_simulated_data') and brain_analyzer.using_simulated_data:
                print("Brain analyzer is using simulated data internally")
        
        print("Successfully initialized brain activity analyzer")
    else:
        brain_analyzer = None
        eyegaze_found = False
        eyegaze_analyzer = None
except Exception as e:
    print(f"Error initializing analyzers: {e}")
    print("Falling back to basic simulation")
    USE_REAL_DATA = False
    brain_analyzer = None
    eyegaze_found = False
    eyegaze_analyzer = None

def get_oscillating_value(speed=0.1, min_val=0.2, max_val=0.8):
    """Get a value that oscillates between min and max using sin wave (fallback for simulation)"""
    return min_val + (max_val - min_val) * (math.sin(time.time() * speed) * 0.5 + 0.5)

def data_generation_loop():
    """Generate brain activity data"""
    global is_generating_data, brain_data, brain_analyzer, using_webcam, eyegaze_found, eyegaze_analyzer
    
    while is_generating_data:
        if USE_REAL_DATA and brain_analyzer:
            # Get eye position from eyegaze dataset if available
            eye_position = "center"  # default
            blink_detected = False   # default
            alertness = "awake"      # default
            
            if eyegaze_found and eyegaze_analyzer:
                # Get the latest eye tracking data with improved reliability
                try:
                    eye_data = eyegaze_analyzer.get_next_reading()
                    eye_position = eye_data.get("eye_position", "center")
                    blink_detected = eye_data.get("blink", False)
                    alertness = eye_data.get("alertness", "awake")
                    
                    # Enhanced logging for debugging
                    if random.random() < 0.01:  # Log occasionally to avoid spam
                        print(f"Eye position: {eye_position}, Blink: {blink_detected}, Alertness: {alertness}")
                except Exception as e:
                    print(f"Error getting eye tracking data: {e}")
            
            # Use the brain analyzer with improved webcam integration
            try:
                if using_webcam:
                    # Process webcam data with enhanced eye position influence
                    reading = brain_analyzer.process_webcam_data(eye_position, blink_detected)
                    
                    # Apply alertness influence to brain activity
                    if alertness == "sleepy":
                        # Make brain activity more balanced/calm when sleepy
                        center_value = (reading["left"] + reading["right"]) / 2
                        reading["left"] = reading["left"] * 0.7 + center_value * 0.3
                        reading["right"] = reading["right"] * 0.7 + center_value * 0.3
                else:
                    reading = brain_analyzer.get_next_reading()
                    # Update the eye position and blink from eyegaze if available
                    if eyegaze_found:
                        reading["eye_position"] = eye_position
                        reading["blink"] = blink_detected
                
                # Add small random variations to create more natural patterns
                reading["left"] += random.uniform(-0.02, 0.02)
                reading["right"] += random.uniform(-0.02, 0.02)
                
                # Keep values in valid range
                reading["left"] = max(0.1, min(1.0, reading["left"]))
                reading["right"] = max(0.1, min(1.0, reading["right"]))
                
                # Update brain state based on current left/right values
                if reading["left"] > reading["right"] + 0.1:
                    reading["state"] = "analytical"
                elif reading["right"] > reading["left"] + 0.1:
                    reading["state"] = "creative"
                else:
                    reading["state"] = "balanced"
                
                brain_data = reading
            except Exception as e:
                print(f"Error processing brain data: {e}")
                # Use previous brain_data or fall back to simulation
                if not brain_data:
                    brain_data = {
                        "left": 0.5,
                        "right": 0.5,
                        "state": "neutral",
                        "eye_position": eye_position,
                        "blink": blink_detected,
                        "timestamp": time.time()
                    }
        else:
            # Enhanced simulation with more natural variation
            time_base = time.time()
            # Use sin waves with different frequencies for natural-looking patterns
            left_activity = 0.5 + 0.3 * math.sin(time_base * 0.2) + 0.1 * math.sin(time_base * 0.5)
            right_activity = 0.5 + 0.3 * math.sin(time_base * 0.15 + 2.0) + 0.1 * math.sin(time_base * 0.45)
            
            # Add small random variations
            left_activity += random.uniform(-0.05, 0.05)
            right_activity += random.uniform(-0.05, 0.05)
            
            # Keep values in valid range
            left_activity = max(0.1, min(0.9, left_activity))
            right_activity = max(0.1, min(0.9, right_activity))
            
            # Determine if this should be a blink moment
            blink_detected = random.random() < 0.05  # 5% chance of blink
            
            # Generate brain state
            if left_activity > right_activity + 0.2:
                state = "analytical"
            elif right_activity > left_activity + 0.2:
                state = "creative"
            else:
                state = "balanced"
            
            # Generate changing eye positions
            eye_position_choices = ["left", "center", "right"]
            eye_position_weights = [0.2, 0.6, 0.2]  # Center is more common
            
            # Change positions more naturally with time-based triggers
            if int(time_base) % 5 == 0 and random.random() < 0.3:  # Every ~5 seconds with 30% chance
                eye_position = random.choices(eye_position_choices, weights=eye_position_weights)[0]
            else:
                eye_position = brain_data.get("eye_position", "center") if brain_data else "center"
                
            # Update global data
            brain_data = {
                "left": left_activity,
                "right": right_activity,
                "state": state,
                "eye_position": eye_position,
                "blink": blink_detected,
                "timestamp": time_base
            }
            
        # Sleep to simulate realistic data rates
        time.sleep(0.1)  # 10Hz update rate

class BrainwaveRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress log messages to keep console clean"""
        pass
        
    def _send_cors_headers(self):
        """Set headers for CORS support"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def _handle_request(self, method):
        """Common handler for GET and POST requests"""
        global device_connected, is_generating_data, generation_thread, brain_data, using_webcam, eyegaze_found, eyegaze_analyzer
        
        # Parse URL path
        path = self.path.split('?')[0]
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        # Handle API routes
        if path == '/api/status':
            response = {
                "status": "ok",
                "version": "1.0.0",
                "device_connected": device_connected,
                "connected": device_connected,  # Add for compatibility with SimpleBrain
                "using_real_data": USE_REAL_DATA
            }
        
        elif path == '/api/dataset_status':
            response = {
                "success": True,
                "hasDataset": USE_REAL_DATA
            }
        
        elif path == '/api/data':
            if not device_connected:
                response = {"error": "Not connected"}
            else:
                response = brain_data
        
        elif path == '/api/mental_state':
            if not device_connected:
                response = {"success": False, "error": "Device not connected"}
            else:
                # Convert to format expected by older frontend code
                response = {
                    "success": True,
                    "data": {
                        "state": brain_data["state"],
                        "confidence": 0.7 + random.uniform(-0.1, 0.1),
                        "left_brain_activity": brain_data["left"],
                        "right_brain_activity": brain_data["right"],
                        "blink_detected": brain_data["blink"],
                        "timestamp": brain_data["timestamp"]
                    }
                }
        
        elif path == '/api/eye_data':
            if not device_connected:
                response = {"success": False, "error": "Not connected"}
            else:
                if eyegaze_found and eyegaze_analyzer:
                    # Get detailed eye data from the eyegaze adapter
                    eye_data = eyegaze_analyzer.get_next_reading()
                    response = {
                        "success": True,
                        "data": eye_data,
                        "using_real_data": not eyegaze_analyzer.using_simulated_data
                    }
                else:
                    # Return simulated or limited eye data
                    response = {
                        "success": True,
                        "data": {
                            "eye_position": brain_data["eye_position"],
                            "blink": brain_data["blink"],
                            "alertness": "awake",  # Default
                            "timestamp": time.time()
                        },
                        "using_real_data": False
                    }
        
        elif path == '/api/webcam_data' and method == 'POST':
            # Handle webcam data input for eye tracking
            if not device_connected:
                response = {"success": False, "error": "Device not connected"}
            else:
                try:
                    # Parse the request body
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    data = json.loads(post_data)
                    
                    # Extract eye tracking data
                    eye_position = data.get('eye_position', 'center')
                    blink_detected = data.get('blink', False)
                    
                    # If using real data and eyegaze is not found, use webcam data
                    if USE_REAL_DATA and brain_analyzer and (using_webcam or not eyegaze_found):
                        # Process webcam data
                        brain_data = brain_analyzer.process_webcam_data(eye_position, blink_detected)
                    else:
                        # Just update the global data
                        brain_data["eye_position"] = eye_position
                        brain_data["blink"] = blink_detected
                    
                    response = {"success": True}
                except Exception as e:
                    response = {"success": False, "error": str(e)}
        
        elif path == '/api/connect' and method == 'POST':
            # Read post data if present
            if 'Content-Length' in self.headers:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                try:
                    request_data = json.loads(post_data)
                    using_webcam = request_data.get('use_webcam', False)
                except:
                    using_webcam = False
            else:
                using_webcam = False
                
            if device_connected:
                response = {"success": False, "error": "already_connected"}
            else:
                device_connected = True
                is_generating_data = True
                
                # Start data generation thread
                generation_thread = threading.Thread(target=data_generation_loop)
                generation_thread.daemon = True
                generation_thread.start()
                
                response = {
                    "success": True,
                    "message": f"Connected successfully using {'webcam-enhanced' if using_webcam else 'EEG-only'} mode",
                    "using_real_data": USE_REAL_DATA
                }
        
        elif path == '/api/disconnect' and method == 'POST':
            device_connected = False
            is_generating_data = False
            response = {"success": True, "message": "Disconnected successfully"}
        
        elif path == '/api/bypass' and method == 'POST' or path == '/api/reset' and method == 'POST':
            device_connected = False
            is_generating_data = False
            response = {"success": True, "message": "Connection state reset successfully"}
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return
        
        # Send JSON response
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        """Handle GET requests"""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self._handle_request('POST')

def run_server(port=5000):
    """Start HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BrainwaveRequestHandler)
    print(f"Starting BCI Interface backend on port {port}...")
    print(f"Using {'REAL CSV DATA' if USE_REAL_DATA else 'SIMULATED DATA'}")
    if USE_REAL_DATA:
        print(f"Place your EEG CSV dataset in: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))}")
    print("Press Ctrl+C to quit")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped")

if __name__ == '__main__':
    run_server()
