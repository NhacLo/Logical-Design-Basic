import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the vehicle control system based on hand gestures.
    """
    gesture_driver = GestureDriver()
    vehicle = ControlBrakeVehicle()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    previous_state = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            timestamp_ms = int(time.time() * 1000)

            # Process the frame to recognize gestures
            state, label, score, landmarks = gesture_driver.process(frame, timestamp_ms)

            # Control the vehicle based on the gesture state, only on state change
            if state != previous_state:
                if state == "GO_AHEAD":
                    print("State changed to GO_AHEAD: Releasing brake.")
                    vehicle.brake_off()
                elif state == "BRAKE_ON":
                    print("State changed to BRAKE_ON: Applying brake.")
                    vehicle.brake_on()
                elif state is None:
                    print("State changed to None: Resetting vehicle.")
                    vehicle.reset()
            
            previous_state = state

            # Display the frame (optional, for debugging)
            # You can add visualization of landmarks here if needed
            cv2.imshow('Gesture Vehicle Control', frame)

            # Exit loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup resources
        print("Exiting application...")
        cap.release()
        cv2.destroyAllWindows()
        # Ensure vehicle is in a safe state on exit
        vehicle.reset()
        print("Application terminated.")

if __name__ == "__main__":
    main()