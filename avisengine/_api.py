# Generated from the AVIS Sandbox's own module (avis-sim: npm run build:python). Do not edit by hand.
import json
import numpy as np
from . import _link as _js

IMAGE_WIDTH = 160
IMAGE_HEIGHT = 120

# Label ids of car.getSemanticLabels(): SEMANTIC_CLASSES[id] is the class name.
SEMANTIC_CLASSES = ["road","lane","sidewalk","building","vegetation","terrain","pole","prop","vehicle","person","ego","sky","trafficSign","trafficLight"]


def _size():
    w, h = _js.get_image_size()
    return int(h), int(w)


class Car:
    """Same method names as the AVIS Engine Python API."""

    def setSpeed(self, speed):
        """0 to 100 percent of max speed (16 m/s). Negative values reverse."""
        _js.set_speed(float(speed))

    def setSteering(self, steering):
        """-100 (full left) to 100 (full right)."""
        _js.set_steering(float(steering))

    def setControl(self, throttle=0.0, steer=0.0, brake=0.0, handBrake=False, reverse=False):
        """Drive directly, like CARLA's VehicleControl: throttle 0..1, steer -1 (left) .. 1 (right), brake 0..1,
        hand brake (rear wheels) and reverse. Replaces the setSpeed speed controller until setSpeed is called again."""
        _js.set_control(float(throttle), float(steer), float(brake), bool(handBrake), bool(reverse))

    def getControl(self):
        """What the car received on the last physics step, after actuator dynamics and driver aids (ABS, traction control):
        {'throttle', 'steer', 'brake', 'handBrake', 'reverse', 'gear'}."""
        return dict(_js.get_control().to_py())

    def getIMU(self):
        """IMU like CARLA's: {'accelerometer': [x, y, z] m/s^2 (specific force, +9.81 up at rest), 'gyroscope': [x, y, z] rad/s,
        'compass': rad (North = 0, clockwise)}. Body axes: x forward, y left, z up. Noise is set in the Sensors window."""
        return json.loads(_js.get_imu())

    def getGNSS(self):
        """GNSS like CARLA's: {'latitude', 'longitude' (degrees), 'altitude' (m)} around the map's geographic origin."""
        return json.loads(_js.get_gnss())

    def getCollisions(self):
        """Collisions since the last call: [{'t', 'other' ('building', 'vehicle' or 'pedestrian'), 'index', 'relativeSpeed', 'impulse', 'x', 'z'}]."""
        return json.loads(_js.get_collisions())

    def getLaneInvasions(self):
        """Lane markings crossed since the last call: [{'t', 's', 'crossed': [{'type' ('Broken', 'Solid', 'SolidSolid'), 'color', 'offset', 'side'}]}]."""
        return json.loads(_js.get_lane_invasions())

    def report(self, **values):
        """Levels that grade an estimate: report it every loop(), e.g. car.report(east=e, north=n).
        Values must be numbers. Other levels ignore it."""
        _js.report(json.dumps({str(k): float(v) for k, v in values.items()}))

    def getLevelData(self):
        """What this level gives you: a path, a speed profile, a start pose... ({} when nothing)."""
        return json.loads(_js.get_level_data())

    def getTransform(self):
        """Ground-truth pose, like CARLA's get_transform: {'x', 'y', 'z' (m), 'yaw', 'pitch', 'roll' (degrees)}.
        Sandbox only: graded levels are about what the sensors see."""
        return _privileged(_js.get_transform())

    def getWaypoints(self, count=20, spacing=2.0):
        """Points on the center of the car's lane ahead, like CARLA's waypoint.next(d): a list of
        {'x', 'z', 'yaw', 's', 'forward', 'left'}; forward and left are in meters in the car's frame.
        Sandbox only."""
        return _privileged(_js.get_waypoints(int(count), float(spacing)))

    def getControlRate(self):
        """How often loop() runs, in Hz of simulation time: 30 in the Sandbox by default (Sensors window), 10 in graded levels.
        Use 1 / car.getControlRate() as your controller's time step."""
        return int(_js.get_control_rate())

    def getSpeed(self):
        """Forward speed in m/s."""
        return float(_js.get_speed())

    def getTime(self):
        """Simulation time in seconds."""
        return float(_js.get_time())

    def getSensors(self):
        """Distance sensors in cm, one per ray of the sensor rig. Default [left, center, right], up to 1500, as in AVIS Engine."""
        return [int(v) for v in _js.get_sensors()]

    def getImage(self):
        """Onboard camera frame, shape (height, width, 3), uint8, BGR like OpenCV. Default (120, 160, 3)."""
        raw = _js.get_image().to_py()
        w, h = _js.get_image_size()
        img = np.frombuffer(raw, dtype=np.uint8).reshape(int(h), int(w), 4)
        return np.ascontiguousarray(img[:, :, 2::-1])

    def getDepth(self):
        """Depth camera as a grayscale image, shape (height, width), uint8: 0 at the camera, 255 at the depth range (50 m by default) or beyond. Same pose and size as getImage()."""
        h, w = _size()
        return np.frombuffer(_js.get_depth().to_py(), dtype=np.uint8).reshape(h, w).copy()

    def getDepthMeters(self):
        """Depth camera in meters, shape (height, width), float32: distance from the camera to each pixel's surface, capped at the depth range."""
        h, w = _size()
        return np.frombuffer(_js.get_depth_meters().to_py(), dtype=np.float32).reshape(h, w).copy()

    def getSemantic(self):
        """Semantic camera as a color image, shape (height, width, 3), uint8, BGR. Each class has one color (Cityscapes style)."""
        h, w = _size()
        img = np.frombuffer(_js.get_semantic().to_py(), dtype=np.uint8).reshape(h, w, 4)
        return np.ascontiguousarray(img[:, :, 2::-1])

    def getSemanticLabels(self):
        """Semantic camera as class ids, shape (height, width), uint8. Names: avisengine.SEMANTIC_CLASSES[id] (road, lane, sidewalk, building, ...)."""
        h, w = _size()
        return np.frombuffer(_js.get_semantic_labels().to_py(), dtype=np.uint8).reshape(h, w).copy()


def _privileged(raw):
    if not raw:
        raise RuntimeError('Ground truth (getTransform, getWaypoints) is not available in graded levels. Use the sensors.')
    return json.loads(raw)


car = Car()

_MAX_WINDOWS = 8
_windows = set()


def imshow(name, img):
    """Show an image in a workspace window. Accepts grayscale, BGR, BGRA or boolean masks."""
    from ._link import to_js
    name = str(name)
    if name not in _windows:
        if len(_windows) >= _MAX_WINDOWS:
            return
        _windows.add(name)
    a = np.asarray(img)
    if a.dtype == bool:
        a = a.astype(np.uint8) * 255
    elif a.dtype != np.uint8:
        a = np.clip(a, 0, 255).astype(np.uint8)
    h, w = a.shape[:2]
    alpha = np.full((h, w), 255, np.uint8)
    if a.ndim == 2:
        rgba = np.dstack([a, a, a, alpha])
    elif a.shape[2] == 3:
        rgba = np.dstack([a[:, :, 2], a[:, :, 1], a[:, :, 0], alpha])
    else:
        rgba = a[:, :, [2, 1, 0, 3]]
    _js.imshow(name, to_js(np.ascontiguousarray(rgba).tobytes()), int(w), int(h))


def _call(fn, raw, w, h, kind):
    """Vision levels: call the student's function on one camera frame (BGR, a fresh copy each time)."""
    w, h = int(w), int(h)
    img = np.frombuffer(raw.to_py(), dtype=np.uint8).reshape(h, w, 4)
    out = fn(np.ascontiguousarray(img[:, :, 2::-1]))
    if kind == 'mask':
        a = np.asarray(out)
        if a.shape != (h, w):
            raise ValueError(f"{fn.__name__}() must return an array of shape ({h}, {w}), not {a.shape}")
        return a.astype(bool).astype(np.uint8).tobytes()

    def plain(v):
        if hasattr(v, 'tolist'):
            return v.tolist()
        if isinstance(v, (list, tuple)):
            return [plain(x) for x in v]
        return v

    return json.dumps(plain(out))


def _call_args(fn, args_json):
    """Function levels: call the student's function with JSON arguments, return JSON."""
    out = fn(*json.loads(args_json))

    def plain(v):
        if hasattr(v, 'tolist'):
            return v.tolist()
        if isinstance(v, (list, tuple)):
            return [plain(x) for x in v]
        if isinstance(v, dict):
            return {str(k): plain(x) for k, x in v.items()}
        return v

    return json.dumps(plain(out))


def _patch_cv2():
    """Route OpenCV's window functions to workspace windows."""
    import cv2
    cv2.imshow = imshow
    cv2.waitKey = lambda *a, **k: -1
    cv2.namedWindow = lambda *a, **k: None
    cv2.destroyAllWindows = lambda *a, **k: None
    cv2.destroyWindow = lambda *a, **k: None
