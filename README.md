# AVIS Engine Python API

A Python API for AVIS Engine (Autonomous Vehicles Intelligent Simulation Software), a robust simulation platform for autonomous vehicle development and testing. It drives both the AVIS Engine desktop simulator and the [AVIS Academy](https://academy.avisengine.com) web Sandbox, which runs in your browser with nothing to download.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Simulator Version](https://img.shields.io/badge/simulator-v2.1.0--beta-orange.svg)](https://avisengine.com)

## Overview

AVIS Engine provides a realistic simulation environment for developing and testing autonomous vehicle algorithms. This Python API allows you to easily interface with the simulator, control vehicles, and collect sensor data.

## Features

- Control vehicle throttle and steering
- Access real-time sensor data (distance sensors, radar, cameras)
- Retrieve vehicle telemetry (speed, position)
- Configure camera settings (FOV, position, resolution) 
- Multiple simulation environments (race track, urban settings)
- Support for semantic segmentation and depth cameras

## Installation

#### Option 1: Using pip

```bash
pip install avisengine
```

#### Option 2: Using git

```bash
git clone https://github.com/AvisEngine/AVIS-Engine-Python-API
cd AVIS-Engine-Python-API
pip install -e .
```

### Simulator

Download the latest simulator from the [AVIS Engine website](https://avisengine.com).

| Version | Link |
|---------|------|
| 2.1.0 (Latest Beta) | [Download](https://avisengine.com) |
| 2.0.1 (Stable) | [Download](https://avisengine.com/v2.0.1) |

## Getting Started

### 1. Launch the Simulator

1. Open the simulator
2. Select a track
3. Click "Open Info Panel"
4. Configure server settings:
   - IP Address (Default: 127.0.0.1)
   - Port (Default: 25001)
5. Click "Start Server"

![Simulator Connection Panel](http://avisengine.com/wp-content/uploads/2021/01/Screen-Shot-2021-01-25-at-1.01.41-AM.png)

### 2. Connect and Control the Vehicle

Here's a basic example to connect to the simulator and control the vehicle:

```python
import avisengine
import config
import time
import cv2

# Create car instance
car = avisengine.Car()

# Connect to simulator
car.connect(config.SIMULATOR_IP, config.SIMULATOR_PORT)

# Wait for connection to establish
time.sleep(3)

try:
    while True:
        # Set throttle (range: -100 to 100)
        car.setSpeed(20)
        
        # Set steering (range: -100 to 100)
        car.setSteering(-10)
        
        # Configure sensors
        car.setSensorAngle(40)
        
        # Get updated data
        car.getData()
        
        # Retrieve sensor data
        sensors = car.getSensors()  # [left, middle, right] distances in cm
        
        # Get camera image (OpenCV format)
        image = car.getImage()
        
        # Get vehicle speed (km/h)
        speed = car.getSpeed()
        
        # Display image
        cv2.imshow('Camera', image)
        if cv2.waitKey(10) == ord('q'):
            break
            
        time.sleep(0.001)
        
finally:
    # Ensure the car stops when the program exits
    car.stop()
```

## The web Sandbox (AVIS Academy)

The [AVIS Academy](https://academy.avisengine.com) Sandbox is a simulator in your browser. This
library lets you drive it from Python on your own computer, with your own editor and libraries
(OpenCV, PyTorch, ROS). You can write the script in either of two ways.

### setup() and loop(), like the Sandbox editor

```python
# my_driver.py
from avisengine import car

def setup():
    car.setSpeed(30)

def loop():
    img = car.getImage()          # numpy array (120, 160, 3), BGR like OpenCV
    sensors = car.getSensors()    # [left, middle, right] in cm
    car.setSteering(0)
```

```bash
python -m avisengine my_driver.py
```

This is the same code as the Sandbox's own editor, with the same API (`getImage`, `getDepth`,
`getSemanticLabels`, `getIMU`, `getGNSS`, `setControl` and more). Each Run in the browser loads
the file again, so edits apply on the next Run. See `example_sandbox.py`.

### A classic loop

Existing scripts work by changing one line:

```python
car = avisengine.Car()
car.connectSandbox()          # instead of car.connect(ip, port)
while True:
    car.setSpeed(20)
    car.getData()             # one simulation step
    image = car.getImage()
```

### Connecting

Both print a port and a six-digit pairing code. In the Sandbox, open **Laptop Python**, enter
them and press **Connect**, then **Run**. The simulator waits for your code at every control step
(each `loop()` call, or each `getData()` call), so results do not depend on how fast your
computer is.

The connection stays on your computer: the script listens on 127.0.0.1 only, accepts only the
AVIS Academy page, and needs the pairing code. Graded practices always run in the browser.

In the Sandbox, `setSpeed` and `setSteering` take percent (-100 to 100), `getSpeed()` on the
classic `Car` is km/h as with the desktop simulator, and `setSensorAngle` is set in the Sandbox's
Sensors window instead.

## API Reference

### Car Class

#### Connection Methods
- `connect(ip, port)` - Connect to the desktop simulator
- `connectSandbox(port=8765)` - Wait for the web Sandbox to connect (prints a pairing code)
- `getData()` - Retrieve the latest data from the simulator
- `stop()` - Stop the car and close the connection

#### Control Methods
- `setSpeed(value)` - Set throttle (-100 to 100)
- `setSteering(value)` - Set steering angle (-100 to 100)
- `setSensorAngle(angle)` - Set the angle between sensor rays

#### Data Retrieval Methods
- `getSensors()` - Returns [left, middle, right] sensor distances in cm
- `getImage()` - Returns camera image as OpenCV compatible array
- `getSpeed()` - Returns current speed in km/h

## Camera Calibration

The simulator includes a checkerboard pattern for camera calibration. Access this feature in simulator version 1.0.5 or higher.

| Calibration Example 1 | Calibration Example 2 |
|-----------------------|-----------------------|
| ![Calibration Example 1](http://avisengine.com/wp-content/uploads/2021/01/Screen-Shot-2020-08-11-at-12.35.39-AM.png) | ![Calibration Example 2](http://avisengine.com/wp-content/uploads/2021/01/Screen-Shot-2020-08-11-at-12.35.52-AM.png) |

## Changelog

### Python API 0.2.0
- Drive the AVIS Academy web Sandbox: `python -m avisengine my_driver.py` (setup/loop) or `car.connectSandbox()` (classic loop)
- Installable package with `pip install avisengine`
- Fewer dependencies (numpy, opencv-python, Pillow, websockets)
- Tests for the desktop protocol and the Sandbox link

### 2.1.0 (Coming Soon)
- ZMQ communication protocol
- Configuration file support
- Configurable camera settings (FOV, position, bird's-eye view)
- Configurable post-processing (DOF, bloom, color corrections)
- Semantic segmentation mode
- Depth camera support
- Radar sensor support
- Pub-sub pattern messaging system

### 2.0.1
- Major API update
- Updated image encoding
- Compressed TCP packets
- Added Utils.py and Config.py
- Added traffic system
- Improved lighting
- Higher resolution camera with better performance
- Adjustable camera resolution
- Message compression algorithm
- Defined `<EOF>` tag in transferred data
- Adjustable front sensor angle
- Added KMP search for `<EOF>` detection

### 2.0.0
- Added new city environment
- Added fog effects
- General improvements

### 1.2.0
- Added localization (English, Persian, Russian, French, German, Chinese, Italian, Spanish, Japanese, Korean, Turkish)
- Visual and performance improvements
- Main menu redesign
- Added "About this simulator" and "Terms of use"

### 1.0.7
- Improved performance
- Added top speed slider
- Added "Right lane Only" toggle
- Added "Visible Sensor detection lines" toggle
- Added angle setting between sensors
- UI/UX improvements
- Improved lighting
- Low-poly vehicle model for better performance
- New checkpoint counting system
- New skyboxes and terrain maps
- Updated textures

### 1.0.6
- Improved tag material contrast (Urban)
- Added borders to signs and tags (Urban)

### 1.0.5
- Fixed raycast hit detection
- Added camera calibration checkerboard
- Added urban track

## License

MIT License - See LICENSE file for details

## Support

For questions, issues, or feature requests:
- [GitHub Issues](https://github.com/AvisEngine/AVIS-Engine-Python-API/issues)
- [Contact Support](https://avisengine.com/contact)

---

Last updated: November 26, 2026
