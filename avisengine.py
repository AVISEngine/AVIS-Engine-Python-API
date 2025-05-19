'''
@ 2025, Copyright AVIS Engine
'''

import cv2
import re
import base64
import time
import socket
import numpy as np
import utils

__author__ = "Amirmohammad Zarif"
__email__ = "amir@avisengine.com"


class Car:
    '''
    AVIS Engine Main Car class
    '''
    def __init__(self) -> None:
        # Instance variables for car state
        self.steering_value: int = 0
        self.speed_value: int = 0
        self.sensor_status: int = 1
        self.image_mode: int = 1
        self.get_Speed: int = 1
        self.sensor_angle: int = 30
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._data_format: str = "Speed:{},Steering:{},ImageStatus:{},SensorStatus:{},GetSpeed:{},SensorAngle:{}"
        self.data_str: str = self._data_format.format(
            self.speed_value, self.steering_value, self.image_mode, self.sensor_status, self.get_Speed, self.sensor_angle
        )
        self.image = None
        self.sensors = None
        self.current_speed = None
        self._is_initialized = False
        self._init_frames_needed = 4  # Number of frames needed for stabilization

    def connect(self, server: str, port: int) -> bool:
        '''
        Connecting to the simulator (server)
        '''
        try:
            self.sock.connect((server, port))
            self.sock.settimeout(5.0)
            print(f"connected to {server} {port}")
            # Give simulator time to initialize
            time.sleep(3)
            # Request initial data frames for stabilization
            for _ in range(self._init_frames_needed):
                self.getData()
            self._is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to connect to {server} {port}: {e}")
            return False

    def recvall(self, sock: socket.socket) -> str:
        '''
        Function to receive all the data chunks
        '''
        BUFFER_SIZE = 131072  # Increased buffer size for better performance
        data = bytearray()
        while True:
            part = sock.recv(BUFFER_SIZE)
            data.extend(part)
            if utils.KMPSearch(b"<EOF>", data) > -1:
                break
        return data.decode("utf-8")

    def setSteering(self, steering: int) -> None:
        '''
        Setting the steering of the car
        '''
        self.steering_value = steering
        self.image_mode = 0
        self.sensor_status = 0
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        time.sleep(0.01)

    def setSpeed(self, speed: int) -> None:
        '''
        Setting the speed of the car
        '''
        self.speed_value = speed
        self.image_mode = 0
        self.sensor_status = 0
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        time.sleep(0.01)

    def setSensorAngle(self, angle: int) -> None:
        '''
        Setting the angle between each sensor ray
        '''
        self.image_mode = 0
        self.sensor_status = 0
        self.sensor_angle = angle
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))

    def getData(self) -> None:
        '''
        Requesting for the data from the simulator
        '''
        self.image_mode = 1
        self.sensor_status = 1
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        receive = self.recvall(self.sock)
        imageTagCheck = re.search('<image>(.*?)<\/image>', receive)
        sensorTagCheck = re.search('<sensor>(.*?)<\/sensor>', receive)
        speedTagCheck = re.search('<speed>(.*?)<\/speed>', receive)
        try:
            if imageTagCheck:
                imageData = imageTagCheck.group(1)
                im_bytes = base64.b64decode(imageData)
                im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
                imageOpenCV = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
                self.image = imageOpenCV
            if sensorTagCheck:
                sensorData = sensorTagCheck.group(1)
                sensor_arr = re.findall("\d+", sensorData)
                sensor_int_arr = list(map(int, sensor_arr))
                self.sensors = sensor_int_arr
            else:
                self.sensors = [1500, 1500, 1500]
            if speedTagCheck:
                current_sp = speedTagCheck.group(1)
                self.current_speed = int(current_sp)
            else:
                self.current_speed = 0
        except Exception as e:
            print(f"Failed to receive data: {e}")

    def getImage(self):
        '''
        Returns the image from the camera
        '''
        return self.image

    def getSensors(self):
        '''
        Returns the sensor data
        '''
        return self.sensors

    def getSpeed(self):
        '''
        Returns the speed of the car
        '''
        return self.current_speed

    def updateData(self) -> None:
        '''
        Updating the request data array and data string
        '''
        data = [self.speed_value, self.steering_value, self.image_mode, self.sensor_status, self.get_Speed, self.sensor_angle]
        self.data_str = self._data_format.format(*data)

    def stop(self) -> None:
        '''
        Stopping the car and closing the socket
        '''
        try:
            self.setSpeed(0)
            self.setSteering(0)
            self.sock.sendall("stop".encode("utf-8"))
            self.sock.close()
            print("Process stopped successfully!")
        except Exception as e:
            print(f"Error during stop: {e}")

    def is_ready(self) -> bool:
        '''
        Check if the car is initialized and ready for operation
        
        Returns
        -------
            bool: True if the car is initialized and ready for operation
        '''
        return self._is_initialized

    def __enter__(self):
        '''Enable use as a context manager.'''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Ensure resources are cleaned up when exiting context.'''
        self.stop()
        return False  # Do not suppress exceptions

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass



