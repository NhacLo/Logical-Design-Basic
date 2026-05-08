import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the gesture-based vehicle control system.
    """
    # Initialize the gesture driver and vehicle control
    driver = GestureDriver()
    vehicle = ControlBrakeVehicle()

    # Initialize video capture from the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    status_text = "INITIALIZING"
    color = (255, 255, 255)  # White

    try:
        while cap.isOpened():
            # Read a frame from the camera
            ret, frame_bgr = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Flip the frame horizontally for a mirror-like view
            frame_bgr = cv2.flip(frame_bgr, 1)

            # Get current timestamp in milliseconds
            timestamp = int(time.time() * 1000)

            # Convert frame from BGR to RGB for the gesture processor
            rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # Process the frame to recognize gestures
            state, label, score, landmarks = driver.process(rgb_frame, timestamp)

            # Control the vehicle based on the gesture state
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
                driver.draw_landmarks(frame_bgr, landmarks)

            # Display the current status on the frame
            cv2.putText(frame_bgr, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Display label and score
            if label and score:
                 cv2.putText(frame_bgr, f"Gesture: {label} ({score:.2f})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


            # Show the final output frame
            cv2.imshow('Gesture Vehicle Control', frame_bgr)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup resources
        print("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        vehicle.reset() # Ensure vehicle is in a safe state on exit
        print("System shut down.")

if __name__ == "__main__":
    main()