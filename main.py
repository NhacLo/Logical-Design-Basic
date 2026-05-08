import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the gesture-based vehicle control system.
    """
    # Initialize the gesture driver, vehicle control, and video capture
    driver = GestureDriver()
    vehicle = ControlBrakeVehicle()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    status_text = "Initializing..."
    color = (255, 255, 255)  # White

    try:
        while cap.isOpened():
            success, frame_bgr = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip the frame horizontally for a later selfie-view display
            frame_bgr = cv2.flip(frame_bgr, 1)

            # Get the current timestamp in milliseconds
            timestamp_ms = int(time.time() * 1000)

            # Convert the BGR frame to RGB for the gesture processor
            rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # Process the frame to get gesture recognition results
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
                # Default state: reset/idle
                vehicle.reset()
                status_text = "RESET / IDLE"
                color = (255, 255, 255) # White

            # Draw landmarks on the BGR frame for visualization
            if landmarks:
                driver.draw_landmarks(frame_bgr, landmarks)

            # Display the status text on the frame
            cv2.putText(frame_bgr, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            if label and score:
                 cv2.putText(frame_bgr, f"Gesture: {label} ({score:.2f})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


            # Display the resulting frame
            cv2.imshow('Gesture Vehicle Control', frame_bgr)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup resources
        print("Cleaning up and shutting down...")
        cap.release()
        cv2.destroyAllWindows()
        vehicle.reset()  # Ensure the vehicle is in a safe (reset) state on exit

if __name__ == "__main__":
    main()