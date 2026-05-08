import cv2
import time
from DMS_Driver import DMSDriver
from VehicleControl import ControlBrakeVehicle
 
def main():
    """
    Main function to run the driver monitoring system and control the vehicle.
    """
    dms = None
    vehicle = None
    cap = None
    try:
        # Initialize DMS Driver, Vehicle Control, and Video Capture
        dms = DMSDriver()
        vehicle = ControlBrakeVehicle()
        cap = cv2.VideoCapture(0)
 
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return
 
        last_status = -1  # Initialize with a value that won't match any status code
 
        print("Starting Driver Monitoring System...")
        print("Press 'q' to quit.")
 
        while True:
            # Capture frame-by-frame
            ret, frame_bgr = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
 
            # Update DMS with the current frame
            output_frame, status_code, status_str = dms.update(frame_bgr)
 
            # Control vehicle based on DMS status, only sending commands on change
            if status_code != last_status:
                if status_code == 0x03:  # DANGER (e.g., eyes closed, drowsiness)
                    vehicle.brake_on()
                    print(f"STATUS CHANGE: DANGER DETECTED ({status_str}). Engaging brake.")
                elif status_code == 0x00:  # NORMAL
                    vehicle.brake_off()
                    print(f"STATUS CHANGE: Driver is NORMAL ({status_str}). Disengaging brake.")
                elif status_code == 0x16:  # WARNING
                    # No brake action for warning, just log it
                    print(f"STATUS CHANGE: WARNING ({status_str}).")
                last_status = status_code
 
            # Display the resulting frame with DMS info
            cv2.imshow('DMS Driver Monitoring', output_frame)
 
            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
 
    except Exception as e:
        print(f"An error occurred: {e}")
 
    finally:
        print("\nExiting program...")
        if cap is not None:
            cap.release()
        if dms is not None:
            dms.close()
        if vehicle is not None:
            vehicle.reset()  # Ensure vehicle is in a safe state on exit
        cv2.destroyAllWindows()
        print("Cleanup complete.")
 
if __name__ == "__main__":