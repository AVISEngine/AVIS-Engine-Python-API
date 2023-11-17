import zmq
import cv2
import numpy as np

context = zmq.Context()
subscriber_socket = context.socket(zmq.SUB)
subscriber_socket.connect("tcp://localhost:5555")

# Subscribe to a specific topic
topic = "CameraFrames"
subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

while True:
    # Receive the topic and encoded frame
    [received_topic, encoded_frame] = subscriber_socket.recv_multipart()

    # Decode the frame
    nparr = np.frombuffer(encoded_frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Process the frame (e.g., display or save it)
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)