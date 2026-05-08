import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the gesture-based vehicle control system.
    """
    # Initialize GestureDriver and ControlBrakeVehicle
    driver = GestureDriver()
    vehicle = ControlBrakeVehicle()

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    status_text = "INITIALIZING"
    color = (255, 255, 255) # White

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            # Get current timestamp in milliseconds
            timestamp_ms = int(time.time() * 1000)

            # Convert the BGR frame to RGB for processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to recognize gestures
            state, label, score, landmarks = driver.process(rgb_frame, timestamp_ms)

            # Control the vehicle based on the recognized gesture state
            if state == "GO_AHEAD":
                vehicle.brake_off()
                status_text = "RUNNING (Brake Off)"
                color = (0, 255, 0)  # Green
            elif state == "BRAKE_ON":
                vehicle.brake_on()
                status_text = "STOPPED (Brake On)"
                color = (0, 0, 255)  # Red
            else:
                vehicle.reset()
                status_text = "RESET / IDLE"
                color = (255, 255, 255) # White

            # Draw landmarks on the BGR frame for visualization
            if landmarks:
                driver.draw_landmarks(frame, landmarks)

            # Display the status text on the frame
            cv2.putText(frame, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Show the frame
            cv2.imshow('Gesture Vehicle Control', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release resources
        print("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        # Ensure vehicle is in a safe state on exit
        vehicle.reset()

if __name__ == "__main__":
    main()