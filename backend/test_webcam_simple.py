import cv2

def test_webcam_simple():
    """Very simple webcam test - just try to open all possible camera indices"""
    print("Testing webcams (press Q to exit each webcam window):")
    
    for camera_index in range(3):
        print(f"\nTrying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"- Failed to open camera {camera_index}")
            continue
        
        print(f"- Success! Camera {camera_index} opened")
        
        # Try to read a frame
        ret, frame = cap.read()
        if not ret:
            print(f"- Camera {camera_index} opened but couldn't read frame")
            cap.release()
            continue
            
        print(f"- Camera {camera_index} is working! (Resolution: {frame.shape[1]}x{frame.shape[0]})")
        print(f"- Showing camera feed in window (press 'q' to close)")
        
        # Show live camera feed until 'q' is pressed
        window_name = f"Camera {camera_index} Test (Press Q to exit)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Add text to the frame
            cv2.putText(frame, f"Camera {camera_index} works! Press 'q' to exit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"- Camera {camera_index} test complete")
        
    print("\nAll webcam tests complete")
    input("Press Enter to exit...")

if __name__ == "__main__":
    print("Simple Webcam Test Tool")
    print("======================")
    print("This will try to open cameras at indices 0, 1, and 2")
    print("A window will open for each working camera found")
    print("Press 'q' to close each camera window and continue testing\n")
    
    try:
        test_webcam_simple()
    except Exception as e:
        print(f"Error during webcam test: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
