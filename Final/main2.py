import cv2
from DMS_Driver import DMSDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the Driver Monitoring System (DMS) for vehicle safety.
    """
    # Initialize the DMS driver and vehicle control
    dms = DMSDriver()
    vehicle = ControlBrakeVehicle()

    # Initialize video capture from the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    last_status = -1  # Initialize with a value that won't match any status code

    try:
        while True:
            # Read a frame from the camera
            ret, frame_bgr = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Flip the frame horizontally for a mirror-like view
            frame_bgr = cv2.flip(frame_bgr, 1)

            # Update the DMS with the new frame
            output_frame, status_code, status_str = dms.update(frame_bgr)

            # Control the vehicle based on the DMS status, only sending command on change
            # 0x03 -> DANGER (e.g., eyes closed, looking down)
            # 0x00 -> NORMAL
            if status_code != last_status:
                if status_code == 0x03:  # DANGER
                    print("DANGER DETECTED: Eyes closed or looking down. Applying brake.")
                    vehicle.brake_on()
                elif status_code == 0x00:  # NORMAL
                    print("Driver is attentive. Releasing brake.")
                    vehicle.brake_off()
                # 0x16 is a WARNING, we don't change the brake state but acknowledge it.
                elif status_code == 0x16:
                    print("WARNING: Driver may be distracted.")

                last_status = status_code

            # Display the output frame from the DMS, which includes visualizations
            cv2.imshow('Driver Monitoring System', output_frame)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup resources
        print("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        if dms:
            dms.close()
        vehicle.reset()  # Ensure vehicle is in a safe state on exit
        print("System shut down.")

if __name__ == "__main__":
    main()