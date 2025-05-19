'''
@ 2025, Copyright AVIS Engine
- An Example Compatible with AVISEngine version 2.0.1 / 1.2.4 (ACL Branch) or higher

This example demonstrates basic usage of the AVIS Engine API:
- Connecting to the simulator
- Controlling the car (speed and steering)
- Reading sensor data
- Processing camera feed
- Displaying real-time FPS
''' 
import avisengine
import config
import time
import cv2
import argparse
import sys

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="AVIS Engine Example Client")
    parser.add_argument('--ip', type=str, default=config.SIMULATOR_IP, help='Simulator IP address')
    parser.add_argument('--port', type=int, default=config.SIMULATOR_PORT, help='Simulator port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for detailed sensor output')
    args = parser.parse_args()

    # Initialize and connect to the simulator using context manager for automatic cleanup
    with avisengine.Car() as car:
        if not car.connect(args.ip, args.port):
            print("Could not connect to simulator. Exiting.")
            sys.exit(1)

        # Initialize control variables
        debug_mode = args.debug
        
        # FPS calculation variables
        prev_time = time.time()
        fps = 0

        try:
            while True:
                # Set car controls
                car.setSpeed(20)  # Set forward speed (range: -100 to 100)
                car.setSteering(-10)  # Turn slightly left (-ve for left, +ve for right)
                car.setSensorAngle(45)  # Set angle between sensor rays
                
                # Request new data from simulator (camera frame, sensors, speed)
                car.getData()

                # Get latest sensor readings and car state
                sensors = car.getSensors()  # Returns [Left, Middle, Right] distances
                image = car.getImage()  # Get camera frame
                carSpeed = car.getSpeed()  # Get current speed in km/h

                # Print debug information if enabled
                if debug_mode:
                    print(f"Speed : {carSpeed}")
                    print(f'Left : {sensors[0]} | Middle : {sensors[1]} | Right : {sensors[2]}')

                # Process and display camera feed if available
                if image is not None and hasattr(image, 'any') and image.any():
                    # Calculate and update FPS
                    curr_time = time.time()
                    fps = 1.0 / (curr_time - prev_time) if prev_time else 0
                    prev_time = curr_time
                    
                    # Draw FPS counter on frame
                    cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    cv2.imshow('frames', image)

                # Check for 'q' key press to quit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
        finally:
            # Clean up OpenCV windows
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()