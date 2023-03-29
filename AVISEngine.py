'''
@ 2023, Copyright AVIS Engine
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


class Car():
    '''
    AVIS Engine Main Car class
    
    Attributes
    ----------

    Public:
        steering_value
        speed_value
        sensor_status
        image_mode
        get_Speed
        data_arr
        data_str
        sock
        image
        sensors
        current_speed
        sensor_angle
    '''

    #Attributes to kind of replicate a Pub-sub pattern messaging to request data  
    steering_value = 0
    speed_value = 0
    sensor_status = 1
    image_mode = 1
    get_Speed = 1
    sensor_angle = 30
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Data format for request
    data_arr = [speed_value, steering_value, image_mode, sensor_status, get_Speed, sensor_angle]
    _data_format = "Speed:{},Steering:{},ImageStatus:{},SensorStatus:{},GetSpeed:{},SensorAngle:{}"
    data_str = _data_format.format(data_arr[0], data_arr[1], data_arr[2], data_arr[3], data_arr[4], data_arr[5])
    
    image = None
    sensors = None
    current_speed = None

    def connect(self,server,port):
        '''
        Connecting to the simulator (server)
        '''
        try:
            self.sock.connect((server, port))
            self.sock.settimeout(5.0)
            
            print("connected to ", server, port)
            return True
        except:
            print("Failed to connect to ", server, port)
            return False

    def recvall(self, socket):
        '''
        Function to receive all the data chunks
        '''
        BUFFER_SIZE = 131072
        data = ""
        while True:
            part = socket.recv(BUFFER_SIZE).decode("utf-8")
            data += part
            # Use KMP search to find the <EOF>, KMPSearch() returns -1 if the pattern was not found
            if(utils.KMPSearch("<EOF>", data) > -1):
                break
            
        return data
        
    def setSteering(self,steering):
        '''
        Setting the steering of the car
        
        Parameters
        ----------
            steering : int
                Steering value in degree
        '''
        self.steering_value = steering
        self.image_mode = 0
        self.sensor_status = 0
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        time.sleep(0.01)

    def setSpeed(self,speed):
        '''
        Setting the speed of the car
        
        Parameters
        ----------
            speed : int
        '''
        self.speed_value = speed
        self.image_mode = 0
        self.sensor_status = 0
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        time.sleep(0.01)

    def setSensorAngle(self, angle):
        '''
        Setting the angle between each sensor ray
        
        Parameters
        ----------
            angle : int
                In degrees
        '''

        self.image_mode = 0
        self.sensor_status = 0
        self.sensor_angle = angle
        self.updateData()
        self.sock.sendall(self.data_str.encode("utf-8"))
        
    def getData(self):
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
            if(imageTagCheck):
                imageData = imageTagCheck.group(1)
                im_bytes = base64.b64decode(imageData)
                im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
                imageOpenCV = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
                self.image = imageOpenCV
            
            if(sensorTagCheck):
                sensorData = sensorTagCheck.group(1)
                sensor_arr = re.findall("\d+", sensorData)
                sensor_int_arr = list(map(int, sensor_arr)) 
                self.sensors = sensor_int_arr
            else:
                self.sensors = [1500,1500,1500]

            if(speedTagCheck):
                current_sp = speedTagCheck.group(1)
                self.current_speed = int(current_sp)
            else:
                self.current_speed = 0
        except:
            print("Failed to receive data")


    def getImage(self):
        '''
        Returns the image from the camera
        '''
        return self.image

    def getSensors(self):
        '''
        Returns the sensor data
            A List: 
                [Left Sensor: int, Middle Sensor: int, Right Sensor: int]
        '''
        return self.sensors
    
    def getSpeed(self):
        '''
        Returns the speed of the car
        '''
        return self.current_speed
    
    def updateData(self):
        '''
        Updating the request data array and data string
        '''
        data = [self.speed_value,self.steering_value,self.image_mode,self.sensor_status,self.get_Speed, self.sensor_angle]
        self.data_str = self._data_format.format(data[0], data[1], data[2], data[3], data[4], data[5])
        
    def stop(self):
        '''
        Stoping the car and closing the socket
        '''
        self.setSpeed(0)
        self.setSteering(0)
        self.sock.sendall("stop".encode("utf-8"))
        self.sock.close()
        print("Process stopped successfully!")
    
    def __del__(self):
        self.stop()
    
        
        
