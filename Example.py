'''
@ 2023, Copyright AVIS Engine
- An Example Compatible with AVISEngine version 2.0.1 or higher
''' 
import avisengine
import config
import time
import cv2

# Creating an instance of the Car class
car = avisengine.Car()

# Connecting to the server (Simulator)
car.connect(config.SIMULATOR_IP, config.SIMULATOR_PORT)

# Counter variable
counter = 0

debug_mode = False

# Sleep for 3 seconds to make sure that client connected to the simulator 
time.sleep(3)

try:
    while(True):
        # Counting the loops
        counter = counter + 1

        # Set the power of the engine the car to 20, Negative number for reverse move, Range [-100,100]
        car.setSpeed(20)

        # Set the Steering of the car -10 degree from center, results the car to steer to the left
        car.setSteering(-10)
        
        # Set the angle between sensor rays to 30 degrees, Use this only if you want to set it from python client
        car.setSensorAngle(40) 

        # Get the data. Need to call it every time getting image and sensor data
        car.getData()

        # Start getting image and sensor data after 4 loops
        if(counter > 4):

            # Returns a list with three items which the 1st one is Left sensor data\
            # the 2nd one is the Middle Sensor data, and the 3rd is the Right one.
            sensors = car.getSensors() 

            # Returns an opencv image type array. if you use PIL you need to invert the color channels.
            image = car.getImage()

            # Returns an integer which is the real time car speed in KMH
            carSpeed = car.getSpeed()

            if(debug_mode):
                print(f"Speed : {carSpeed}") 
                print(f'Left : {str(sensors[0])} | Middle : {str(sensors[1])} | Right : {str(sensors[2])}')
            
            # Showing the opencv type image
            cv2.imshow('frames', image)


            if cv2.waitKey(10) == ord('q'):
                break

            time.sleep(0.001)

finally:
    car.stop()