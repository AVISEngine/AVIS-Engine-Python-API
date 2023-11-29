import zmq

def subscribe(topic):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://127.0.0.1:25005")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    while True:
        topic = subscriber.recv_string()
        message = subscriber.recv_string()
        print(f"Received message on topic {topic}: {message}")

if __name__ == "__main__":
    subscribe("/car/steering")
    # Add more topics as needed
    