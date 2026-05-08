from vehicle_motion_api import VehicleMotionAPI
import time
import rospy

def main():
    """
    Main function
    """
    vm_api = VehicleMotionAPI()
    try:
        while (not vm_api.exit_flag):
            """ Begin application code """
            time.sleep(0.01)
            """ End application code """
    except KeyboardInterrupt:
        print("Shutting down")
if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    