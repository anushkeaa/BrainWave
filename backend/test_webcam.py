import cv2
import time
import sys
import traceback

def test_webcam_and_display_stream():
    """Test webcam by showing live feed with face detection"""
    print("\n======== WEBCAM TEST RUNNING ========")
    print("If you see your webcam feed in a window, your webcam is working correctly!")
    print("Press 'q' to quit the webcam test when you're done")
    print("=======================================\n")
    
    # Try to load face detection cascade
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        face_detection = True
        print("Face detection enabled - your face should be highlighted with a blue box")
    except Exception as e:
        face_detection = False
        print(f"Face detection not available: {e}")
    
    # Try each camera index
    for camera_index in range(3):
        print(f"Trying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"Could not open camera {camera_index}")
            continue
            
        print(f"SUCCESS! Opened camera {camera_index}")
        
        # Create window
        window_name = f"WEBCAM RUNNING - Press 'q' to quit"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Show live feed
        start_time = time.time()
        frame_count = 0
        success = False
        
        try:
            while True:
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                    
                success = True
                frame_count += 1
                
                # Detect faces if enabled
                if face_detection:
                    try:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                        
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    except Exception as e:
                        print(f"Error in face detection: {e}")
                
                # Add text to the frame
                cv2.putText(frame, "Webcam working! Press 'q' to exit", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show frame
                cv2.imshow(window_name, frame)
                
                # Break on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Error during webcam display: {e}")
            traceback.print_exc()
        
        # Release and cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        if success:
            print(f"Webcam test successful for camera {camera_index}")
            print("Your webcam is working correctly!")
            return True
    
    print("No working webcam found. Please check your connections and privacy settings.")
    return False

if __name__ == "__main__":
    print("\n==== DIRECT WEBCAM TEST ====")
    print("Testing your webcam directly...")
    try:
        result = test_webcam_and_display_stream()
        if not result:
            print("\nNo webcam detected. Please try:")
            print("1. Check your webcam is connected properly")
            print("2. Make sure no other app is using your webcam")
            print("3. Check your privacy settings to allow camera access")
    except Exception as e:
        print(f"Error running webcam test: {e}")
        traceback.print_exc()
    
    print("\nTest complete. Press Enter to close this window...")
    input()
