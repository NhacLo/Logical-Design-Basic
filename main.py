import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    # Initialize the recognizer and the UDP control sender
    driver = GestureDriver()
    vehicle = ControlBrakeVehicle()
    
    # Initialize camera (Raspberry Pi 4 or Jetson Nano)
    cap = cv2.VideoCapture(0)
    
    print("System Online. Controls:")
    print("- Pointing_Up -> RUN (Brake Off)")
    print("- Closed_Fist -> STOP (Brake On)")
    print("- No Hand/Unknown -> RESET")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert BGR to RGB for MediaPipe processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            timestamp = int(time.time() * 1000)

            # 1. Process the frame for gestures
            state, label, score, landmarks = driver.process(rgb_frame, timestamp)

            # 2. Logic for Vehicle Control
            if state == "GO_AHEAD":
                # 'Pointing_Up' sends 0x00 to release the brake
                vehicle.brake_off() 
                status_text = "RUNNING (Brake Off)"
                color = (0, 255, 0)
            elif state == "BRAKE_ON":
                # 'Closed_Fist' sends 0x01 to apply the brake
                vehicle.brake_on()
                status_text = "STOPPED (Brake On)"
                color = (0, 0, 255)
            else:
                # No hand detected or unknown gesture sends 0x02
                vehicle.reset()
                status_text = "RESET / IDLE"
                color = (255, 255, 255)

            # 3. Visual Feedback for Thesis Presentation
            driver.draw_landmarks(frame, landmarks)
            cv2.putText(frame, status_text, (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            cv2.imshow('Driver Monitoring System', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Cleanup and safety reset
        cap.release()
        cv2.destroyAllWindows()
        driver.close()
        vehicle.reset()

if __name__ == "__main__":
    main()