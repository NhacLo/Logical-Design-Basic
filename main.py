import cv2
from DMS_Driver import DMSDriver
from VehicleControl import ControlBrakeVehicle

def main():
    """
    Main function to run the Driver Monitoring System (DMS) for vehicle control.
    """
    # Initialize DMSDriver, VehicleControl, and video capture
    dms = DMSDriver()
    vehicle = ControlBrakeVehicle()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    last_status = None # To track status changes and avoid command spam

    try:
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            # The DMS driver processes the BGR frame directly
            output_frame, status_code, status_str = dms.update(frame_bgr)

            # Control vehicle based on DMS status code, only on change
            # 0x03 -> DANGER (e.g., eye close, look down)
            # 0x00 -> NORMAL
            # 0x16 -> WARNING
            if status_code != last_status:
                if status_code == 0x03: # DANGER
                    print("DANGER DETECTED: Eyes closed or looking down. Engaging brake.")
                    vehicle.brake_on()
                elif status_code == 0x00: # NORMAL
                    print("Driver is attentive. Releasing brake.")
                    vehicle.brake_off()
                # For 0x16 (WARNING), we don't send a brake command, just log.
                elif status_code == 0x16:
                    print("WARNING: Driver may be distracted.")

                last_status = status_code

            # Display the output frame from the DMS driver
            # It includes visualizations and status information
            cv2.imshow('Driver Monitoring System', output_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Cleanup
        print("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        if dms:
            dms.close()
        vehicle.reset() # Ensure vehicle is in a safe state on exit

if __name__ == "__main__":
    main()