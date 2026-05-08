import cv2
import time
from gesture_driver import GestureDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the gesture-based vehicle control system.
    """
    driver = None
    vehicle = None
    cap = None
    try:
        # Initialize GestureDriver, VehicleControl, and camera capture
        driver = GestureDriver()
        vehicle = ControlBrakeVehicle()
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return

        # Initial status
        status_text = "INITIALIZING"
        color = (255, 255, 255)

        print("System Initialized. Point hand to the camera. Press 'q' to quit.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Get current timestamp in milliseconds
            timestamp = int(time.time() * 1000)

            # Convert frame from BGR to RGB for processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to get gesture state
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
            else:
                # Default idle/reset state
                vehicle.reset()
                status_text = "RESET / IDLE"
                color = (255, 255, 255) # White

            # Draw landmarks on the BGR frame for visualization
            if landmarks:
                driver.draw_landmarks(frame, landmarks)
            
            # Display the current status on the frame
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            if label and score:
                 cv2.putText(frame, f"Gesture: {label} ({score:.2f})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

            # Show the frame
            cv2.imshow('Gesture Vehicle Control', frame)

            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit signal received. Shutting down.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        if vehicle:
            print("Resetting vehicle state.")
            vehicle.reset()
        print("System shutdown complete.")

if __name__ == "__main__":
    main()