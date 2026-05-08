import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the gesture-based vehicle control system.
    """
    # Initialize GestureDriver, VehicleControl, and video capture
    driver = GestureDriver()
    vehicle = ControlBrakeVehicle()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    status_text = "Initializing..."
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
            timestamp = int(time.time() * 1000)

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame for gesture recognition
            state, label, score, landmarks = driver.process(rgb_frame, timestamp)

            # Control vehicle based on gesture state
            if state == "GO_AHEAD":
                vehicle.brake_off()
                status_text = "RUNNING (Brake Off)"
                color = (0, 255, 0)  # Green
            elif state == "BRAKE_ON":
                vehicle.brake_on()
                status_text = "STOPPED (Brake On)"
                color = (0, 0, 255)  # Red
            else: # None or other states
                vehicle.reset()
                status_text = "RESET / IDLE"
                color = (255, 255, 255) # White

            # Draw landmarks on the BGR frame for visualization
            if landmarks:
                driver.draw_landmarks(frame, landmarks)

            # Display status text on the frame
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            if label and score:
                 cv2.putText(frame, f"Gesture: {label} ({score:.2f})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


            # Display the resulting frame
            cv2.imshow('Gesture Vehicle Control', frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup
        print("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        vehicle.reset() # Ensure vehicle is in a safe state on exit

if __name__ == "__main__":
    main()