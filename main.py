import cv2
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    gesture_driver = GestureDriver()
    vehicle = ControlBrakeVehicle()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Starting gesture control system...")
    print("GO_AHEAD gesture -> brake off (vehicle run)")
    print("BRAKE_ON gesture -> brake on (vehicle stop)")
    print("No hand/unknown -> reset vehicle")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
        
        state, label, score, landmarks = gesture_driver.process(frame, timestamp_ms)
        
        if state == "GO_AHEAD":
            vehicle.brake_off()
            status = "Vehicle Running"
        elif state == "BRAKE_ON":
            vehicle.brake_on()
            status = "Vehicle Stopped"
        else:
            vehicle.reset()
            status = "Vehicle Reset"
        
        display_text = f"State: {state if state else 'None'} | Status: {status}"
        cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Gesture Control', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vehicle.reset()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()