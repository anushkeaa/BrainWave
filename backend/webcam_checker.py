import sys
import traceback

def check_webcam():
    """
    Comprehensive webcam check script that outputs detailed diagnostic information
    """
    print("Running webcam diagnostics...")
    
    # Step 1: Check OpenCV installation
    try:
        import cv2
        print("✓ OpenCV installed successfully (version:", cv2.__version__, ")")
    except ImportError:
        print("✗ OpenCV not installed. Please run: pip install opencv-python")
        return False
    
    # Step 2: Try to access webcam
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("✗ Could not open webcam with index 0")
            
            # Try alternative camera indices
            for i in range(1, 3):
                print(f"  Trying alternative webcam (index {i})...")
                alt_cap = cv2.VideoCapture(i)
                if alt_cap.isOpened():
                    print(f"✓ Successfully opened webcam with index {i}")
                    alt_cap.release()
                    print("  You should modify eye_blink_detector.py to use this index")
                    return True
                alt_cap.release()
                
            print("✗ No webcam could be opened on any index")
            print("  Webcam troubleshooting tips:")
            print("  - Check if webcam is properly connected")
            print("  - Verify webcam is not in use by another application")
            print("  - Check device manager to ensure webcam is working properly")
            print("  - Try restarting your computer")
            return False
        else:
            # Successfully opened webcam, test reading a frame
            ret, frame = cap.read()
            if ret:
                print(f"✓ Successfully captured frame from webcam (shape: {frame.shape})")
                height, width, channels = frame.shape
                print(f"  Resolution: {width}x{height}, Channels: {channels}")
                
                # Try to detect faces to validate Haar cascades
                try:
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    print(f"  Face detection test: {len(faces)} faces detected")
                except Exception as e:
                    print(f"  Face detection test failed: {e}")
            else:
                print("✗ Failed to capture frame from webcam")
                
            cap.release()
            return True
    except Exception as e:
        print(f"✗ Error accessing webcam: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_webcam()
    print("\nDiagnostic summary:", "PASSED" if success else "FAILED")
    print("Run this script from command line for detailed diagnostics:")
    print("python webcam_checker.py")
