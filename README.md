# AVIS Engine Python API

A Python API for AVIS Engine (Autonomous Vehicles Intelligent Simulation Software) - a robust simulation platform for autonomous vehicle development and testing.

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
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

### Requirements

```bash
pip install -r requirements.txt
```

### Python API

#### Option 1: Using git

```bash
git clone https://github.com/AvisEngine/AVIS-Engine-Python-API
cd AVIS-Engine-Python-API
```

#### Option 2: Using pip (Coming soon)

```bash
pip install avisengine
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

## API Reference

### Car Class

#### Connection Methods
- `connect(ip, port)` - Connect to the simulator
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

Last updated: May 19, 2025
