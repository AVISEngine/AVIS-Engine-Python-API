# AVIS Engine Python API Documentation

The AVIS Engine Python API provides a robust interface for controlling and interacting with the AVIS Engine Simulator for autonomous vehicle development.

## Installation

```bash
pip install avisengine
```

## Quick Start

```python
from avisengine import Car

# Create a car instance
car = Car()

# Connect to the simulator
car.connect("localhost", 25001)

# Set speed and steering
car.setSpeed(50)
car.setSteering(0)

# Get sensor data
sensors = car.getSensors()
print(f"Sensor readings: {sensors}")

# Get camera image
image = car.getImage()

# Stop the car and close connection
car.stop()
```

## API Reference

### Car Class

The main class for interacting with the AVIS Engine simulator.

#### Methods

- `connect(server, port)`: Connect to the simulator
- `setSpeed(speed)`: Set the car's speed
- `setSteering(steering)`: Set the steering angle
- `setSensorAngle(angle)`: Set the angle between sensor rays
- `getData()`: Request and update sensor data
- `getImage()`: Get the current camera image
- `getSensors()`: Get the current sensor readings
- `getSpeed()`: Get the current speed
- `stop()`: Stop the car and close the connection
