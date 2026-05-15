import cv2
import time
from DMS_Driver import DMSDriver
from Vehicle_Control import ControlBrakeVehilce

def main():
    # 1. Initialize the APIs
    # DMSDriver handles face landmarking and behavior logic
    dms = DMSDriver()
    # ControlBrakeVehilce handles UDP communication with the vehicle's braking system
    vehicle = ControlBrakeVehilce()

    # 2. Setup Video Capture (Webcam)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("System Started. Monitoring driver behavior...")
    
    # Track the last sent command to avoid spamming the network
    last_status = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 3. Process the frame through DMS
            # returns: processed frame (with overlays), hex status code, and status string
            output_frame, status_code, status_str = dms.update(frame)

            # 4. Monitor Behavior and Control Vehicle
            # Status Logic:
            # 0x03 (DANGER)  -> Activate Brakes
            # 0x16 (WARNING) -> Alert driver (Visual text already in output_frame)
            # 0x00 (NORMAL)  -> Release Brakes
            
            if status_str != last_status:
                if status_code == 0x03:  # DANGER
                    print(f"!!! ALERT: {status_str} detected. Applying brakes.")
                    vehicle.brake_on()
                elif status_code == 0x00:  # NORMAL
                    print(f"Status: {status_str}. Releasing brakes/Normal operation.")
                    vehicle.brake_off()
                elif status_code == 0x16:  # WARNING
                    print(f"Warning: {status_str}. Driver is distracted.")
                    # In a real scenario, you might trigger a buzzer here
                
                last_status = status_str

            # 5. Display the output
            cv2.imshow("DMS - Driver Monitoring System", output_frame)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("System interrupted by user.")
    finally:
        # 6. Cleanup
        cap.release()
        cv2.destroyAllWindows()
        dms.close()
        # Reset vehicle state to safe mode on exit
        vehicle.reset()

if __name__ == "__main__":
    main()