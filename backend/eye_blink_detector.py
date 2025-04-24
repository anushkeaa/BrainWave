import cv2
import numpy as np
import time
import threading
from queue import Queue
import sys

class EyeBlinkDetector:
    """
    Detect eye blinks using computer vision with OpenCV.
    Uses facial landmarks to track the eye aspect ratio (EAR).
    """
    def __init__(self):
        self.running = False
        self.thread = None
        self.blink_queue = Queue(maxsize=100)
        self.last_blink_time = 0
        self.blink_count = 0
        self.left_blink_count = 0
        self.right_blink_count = 0
        self.last_prediction = None
        
        # Load required models
        self.face_cascade = None
        self.eye_cascade = None
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize OpenCV face and eye detection models."""
        try:
            # Load Haar cascades for face and eye detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            print("Face and eye detection models loaded successfully")
        except Exception as e:
            print(f"Error loading face/eye detection models: {e}")
    
    def start_detection(self):
        """Start eye blink detection in a separate thread."""
        if self.running:
            print("Eye blink detection already running")
            return False
            
        if self.face_cascade is None or self.eye_cascade is None:
            print("Face or eye detection models not loaded properly")
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._detection_worker)
        self.thread.daemon = True
        self.thread.start()
        print("Eye blink detection started")
        return True
    
    def stop_detection(self):
        """Stop eye blink detection."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        print("Eye blink detection stopped")
        
    def _detection_worker(self):
        """Worker thread for eye blink detection."""
        # Initialize video capture from webcam - try multiple camera indices
        try:
            # Try to use the global CAMERA_INDEX if available
            camera_index = getattr(sys.modules['__main__'], 'CAMERA_INDEX', 0)
            
            # Try camera indices 0, 1, 2 if the first one fails
            success = False
            for i in range(3):
                try:
                    idx = (camera_index + i) % 3  # Start with preferred index, then try others
                    print(f"Attempting to open webcam at index {idx}...")
                    cap = cv2.VideoCapture(idx)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            print(f"Successfully opened webcam at index {idx}")
                            success = True
                            break
                        else:
                            print(f"Could open camera {idx} but couldn't read frames")
                            cap.release()
                    else:
                        print(f"Failed to open camera at index {idx}")
                except Exception as e:
                    print(f"Error with camera index {idx}: {e}")
            
            if not success:
                print("Error: Could not open any webcam")
                self.running = False
                return
                
            # Variables for blink detection - more sensitive settings
            eye_open_threshold = 5  # Reduced from 10 to make detection more sensitive
            eyes_detected_frames = 0
            eyes_not_detected_frames = 0
            blink_threshold = 2  # Reduced from 3 to detect blinks faster
            left_eye_positions = []
            right_eye_positions = []
            
            print("Webcam opened successfully, starting detection loop")
            
            # Set webcam properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            while self.running:
                # Read frame from webcam
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame from webcam")
                    break
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Improve contrast
                gray = cv2.equalizeHist(gray)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=4,  # Reduced from 5 for better detection
                    minSize=(30, 30)
                )
                
                # If faces are detected, look for eyes
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        # Create region of interest for the face
                        roi_gray = gray[y:y+h, x:x+w]
                        
                        # Detect eyes in the face ROI
                        eyes = self.eye_cascade.detectMultiScale(
                            roi_gray,
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(20, 20)
                        )
                        
                        # If eyes are detected, track them
                        if len(eyes) >= 2:
                            eyes_detected_frames += 1
                            eyes_not_detected_frames = 0
                            
                            # Sort eyes by x-coordinate to determine left vs. right
                            eyes = sorted(eyes, key=lambda e: e[0])
                            
                            # Process left eye
                            left_eye = eyes[0]
                            left_eye_pos = (x + left_eye[0] + left_eye[2]//2, y + left_eye[1] + left_eye[3]//2)
                            left_eye_positions.append(left_eye_pos)
                            
                            # Process right eye
                            right_eye = eyes[1]
                            right_eye_pos = (x + right_eye[0] + right_eye[2]//2, y + right_eye[1] + right_eye[3]//2)
                            right_eye_positions.append(right_eye_pos)
                            
                            # Keep only the most recent positions
                            if len(left_eye_positions) > 10:
                                left_eye_positions.pop(0)
                                right_eye_positions.pop(0)
                            
                        else:
                            eyes_not_detected_frames += 1
                            eyes_detected_frames = 0
                            
                            # If eyes were detected before but not now, it might be a blink
                            if eyes_not_detected_frames == blink_threshold and eyes_detected_frames > eye_open_threshold:
                                # We detected a blink
                                self.blink_count += 1
                                current_time = time.time()
                                
                                # Determine if it's a left or right eye blink based on recent history
                                if left_eye_positions and right_eye_positions:
                                    left_movement = self._calculate_movement(left_eye_positions)
                                    right_movement = self._calculate_movement(right_eye_positions)
                                    
                                    if left_movement > right_movement * 1.2:  # Left eye moved more
                                        self.left_blink_count += 1
                                        blink_type = 'left'
                                    elif right_movement > left_movement * 1.2:  # Right eye moved more
                                        self.right_blink_count += 1
                                        blink_type = 'right'
                                    else:  # Both eyes moved similarly
                                        blink_type = 'both'
                                else:
                                    blink_type = 'both'
                                    
                                # Update prediction based on recent blink history
                                left_ratio = self.left_blink_count / max(1, self.blink_count)
                                
                                if left_ratio > 0.6:  # More left eye movement
                                    prediction = 'right'  # Right brain is more active
                                    confidence = 0.5 + (left_ratio - 0.5)
                                elif left_ratio < 0.4:  # More right eye movement
                                    prediction = 'left'  # Left brain is more active
                                    confidence = 0.5 + (0.5 - left_ratio)
                                else:  # Balanced
                                    prediction = 'neutral'
                                    confidence = 0.5
                                    
                                # Add blink detection to queue
                                try:
                                    self.blink_queue.put({
                                        'time': current_time,
                                        'type': blink_type,
                                        'prediction': prediction,
                                        'confidence': confidence
                                    }, block=False)
                                    
                                    self.last_prediction = {
                                        'state': prediction,
                                        'confidence': confidence
                                    }
                                    
                                    print(f"Blink detected! Type: {blink_type}, Prediction: {prediction}")
                                except:
                                    pass  # Queue full, skip this blink
                                
                                # Reset counters
                                eyes_detected_frames = 0
                                eyes_not_detected_frames = 0
                                left_eye_positions = []
                                right_eye_positions = []
                
                # Slow down the processing to not overuse CPU
                time.sleep(0.05)
                
            # Release webcam when done
            cap.release()
            print("Webcam released, detection stopped")
            
        except Exception as e:
            print(f"Error in eye blink detection: {e}")
            self.running = False
    
    def _calculate_movement(self, positions):
        """Calculate the amount of movement from position history."""
        if len(positions) < 2:
            return 0
            
        total_movement = 0
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            movement = (dx**2 + dy**2)**0.5  # Euclidean distance
            total_movement += movement
            
        return total_movement
    
    def get_latest_blink(self):
        """Get the latest blink detection."""
        try:
            return self.blink_queue.get(block=False)
        except:
            return None
    
    def get_current_prediction(self):
        """Get the current prediction based on blink history."""
        return self.last_prediction
    
    def is_running(self):
        """Check if detection is running."""
        return self.running

# For testing
if __name__ == "__main__":
    detector = EyeBlinkDetector()
    detector.start_detection()
    
    try:
        print("Eye blink detector running. Press Ctrl+C to stop.")
        while True:
            blink = detector.get_latest_blink()
            if blink:
                print(f"Blink detected: {blink}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping eye blink detector...")
    finally:
        detector.stop_detection()
