from gesture_driver import GestureDriver
from Vehicle_Control import ControlBrakeVehilce
import cv2

def main():
    # Initialize gesture driver and vehicle control
    gesture_driver = GestureDriver()
    vehicle = ControlBrakeVehilce()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    print("Gesture Control Started...")
    print("Pointing -> Vehicle Run")
    print("Hold Hand -> Vehicle Stop")
    print("No Hand/Unknown -> Reset Vehicle")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get gesture recognition result
        gesture_result = gesture_driver.recognize(frame)
        
        # Control vehicle based on gesture
        if gesture_result == "GO_AHEAD":
            vehicle.brake_off()
            print("Gesture: Pointing -> Vehicle Running")
        elif gesture_result == "BRAKE_ON":
            vehicle.brake_on()
            print("Gesture: Hold Hand -> Vehicle Stopped")
        else:
            vehicle.reset()
            print("Gesture: None/Unknown -> Vehicle Reset")
        
        # Display frame
        cv2.imshow("Gesture Control", frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    vehicle.reset()

if __name__ == "__main__":
    main()