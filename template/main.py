import cv2
import numpy as np
from gesture_driver import GestureDetector
from Vehicle_Control import VehicleControl

def main():
    # Initialize gesture detector and vehicle control
    gesture_detector = GestureDetector()
    vehicle = VehicleControl()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    print("Gesture Control System Started")
    print("Pointing -> Vehicle Run")
    print("Open Hand -> Vehicle Stop")
    print("No Hand/Unknown -> Reset Vehicle")
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Detect gesture
            gesture = gesture_detector.detect(frame)
            
            # Control vehicle based on gesture
            if gesture == "GO_AHEAD":
                print("Gesture: Pointing -> Vehicle Running")
                vehicle.brake_off()
            elif gesture == "BRAKE_ON":
                print("Gesture: Open Hand -> Vehicle Stopped")
                vehicle.brake_on()
            else:
                print("Gesture: None/Unknown -> Vehicle Reset")
                vehicle.reset()
            
            # Display frame (optional)
            cv2.imshow("Gesture Control", frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping gesture control system...")
    
    finally:
        # Cleanup
        vehicle.reset()
        cap.release()
        cv2.destroyAllWindows()
        print("System stopped safely")

if __name__ == "__main__":
    main()