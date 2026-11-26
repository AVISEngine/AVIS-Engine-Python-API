"""
The link to the AVIS Sandbox in the browser: the same functions the in-browser `avisengine`
calls (`_avis_js`), carried over a local WebSocket. The browser answers each call from the
simulator; setters are sent without waiting for an answer.

Messages (JSON text frames, raw bytes as binary frames that follow their JSON message):
  laptop -> browser  {"t": "call", "fn", "args", "bins", "id"?}   (no id: no answer wanted)
  browser -> laptop  {"t": "ret", "id", "value"} or {"t": "ret", "id", "bin": true} + bytes
"""
import itertools
import json


class Stopped(Exception):
    """The browser stopped the run (Stop button, reset, closed tab)."""


_ws = None
_ids = itertools.count(1)


class _Bytes(bytes):
    """Raw bytes from the browser; .to_py() mirrors Pyodide's JsProxy so the shared module works unchanged."""

    def to_py(self):
        return bytes(self)


class _Dict(dict):
    def to_py(self):
        return dict(self)


def to_js(b):
    return b


def attach(ws):
    global _ws
    _ws = ws


def _call(fn, *args, wait=True):
    if _ws is None:
        raise RuntimeError('Not connected to the AVIS Sandbox. Run your script with: python -m avisengine your_script.py')
    plain, bins = [], []
    for a in args:
        if isinstance(a, (bytes, bytearray, memoryview)):
            plain.append({'$bin': len(bins)})
            bins.append(bytes(a))
        else:
            plain.append(a)
    msg = {'t': 'call', 'fn': fn, 'args': plain, 'bins': len(bins)}
    call_id = next(_ids) if wait else None
    if wait:
        msg['id'] = call_id
    _ws.send(json.dumps(msg))
    for b in bins:
        _ws.send(b)
    if not wait:
        return None
    while True:
        raw = _ws.recv()
        if isinstance(raw, bytes):
            continue
        r = json.loads(raw)
        if r.get('t') == 'ret' and r.get('id') == call_id:
            if r.get('bin'):
                return _Bytes(_ws.recv())
            return r.get('value')
        if r.get('t') == 'stop':
            raise Stopped()


def _send(fn):
    return lambda *a: _call(fn, *a, wait=False)


def _ask(fn):
    return lambda *a: _call(fn, *a)


set_speed = _send('set_speed')
set_steering = _send('set_steering')
set_control = _send('set_control')
report = _send('report')
imshow = _send('imshow')

get_speed = _ask('get_speed')
get_time = _ask('get_time')
get_image = _ask('get_image')
get_sensors = _ask('get_sensors')
get_image_size = _ask('get_image_size')
get_transform = _ask('get_transform')
get_waypoints = _ask('get_waypoints')
get_control_rate = _ask('get_control_rate')
get_imu = _ask('get_imu')
get_gnss = _ask('get_gnss')
get_collisions = _ask('get_collisions')
get_lane_invasions = _ask('get_lane_invasions')
get_depth = _ask('get_depth')
get_depth_meters = _ask('get_depth_meters')
get_semantic = _ask('get_semantic')
get_semantic_labels = _ask('get_semantic_labels')
get_level_data = _ask('get_level_data')


def get_control():
    return _Dict(_call('get_control') or {})
