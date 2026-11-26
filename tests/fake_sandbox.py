"""A stand-in for the AVIS Sandbox page: connects like the browser and answers car calls from a tiny fake sim."""
import json
import socket
import threading
import time

import numpy as np
from websockets.sync.client import connect

ORIGIN = 'http://localhost:5174'

try:  # websockets 15+ asks for legacy=True to connect without a with-block
    import inspect

    _LEGACY = 'legacy' in inspect.signature(connect).parameters
except (TypeError, ValueError):
    _LEGACY = False


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_port(port, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                return
        time.sleep(0.05)
    raise TimeoutError(f'nothing listening on {port}')


class FakeSandbox:
    """Sim state the script can change and read; records every call."""

    def __init__(self, port, code, origin=ORIGIN):
        wait_port(port)
        self.ws = connect(f'ws://127.0.0.1:{port}', origin=origin, compression=None, legacy=True) if _LEGACY else connect(f'ws://127.0.0.1:{port}', origin=origin, compression=None)
        self.ws.send(json.dumps({'t': 'hello', 'code': code}))
        self.welcome = json.loads(self.ws.recv(timeout=10))
        self.speed_cmd = 0.0
        self.steer_cmd = 0.0
        self.time = 0.0
        self.calls = []
        self.history = []  # (fn, first argument) of every command
        self.prints = []
        # A camera frame with a recognizable pixel: row 60, column 80 is (B, G, R) = (10, 20, 30).
        rgba = np.zeros((120, 160, 4), np.uint8)
        rgba[60, 80] = [30, 20, 10, 255]
        self.rgba = rgba.tobytes()

    def _answer(self, msg):
        fn = msg['fn']
        args = msg.get('args', [])
        self.calls.append(fn)
        if fn.startswith('set_'):
            self.history.append((fn, args[0] if args else None))
        if fn == 'set_speed':
            self.speed_cmd = args[0]
        elif fn == 'set_steering':
            self.steer_cmd = args[0]
        if 'id' not in msg:
            return
        value = {
            'get_image_size': [160, 120],
            'get_sensors': [1500, 700, 1500],
            'get_speed': self.speed_cmd / 10.0,
            'get_time': self.time,
            'get_control_rate': 30,
        }.get(fn)
        if fn == 'get_image':
            self.ws.send(json.dumps({'t': 'ret', 'id': msg['id'], 'bin': True}))
            self.ws.send(self.rgba)
        else:
            self.ws.send(json.dumps({'t': 'ret', 'id': msg['id'], 'value': value}))

    def request(self, kind):
        """Send setup or loop and answer calls until done; returns the error or None."""
        self.ws.send(json.dumps({'t': kind}))
        while True:
            raw = self.ws.recv(timeout=10)
            if isinstance(raw, bytes):
                continue
            m = json.loads(raw)
            if m['t'] == 'call':
                for _ in range(m.get('bins', 0)):
                    self.ws.recv(timeout=10)
                self._answer(m)
            elif m['t'] == 'print':
                self.prints.append(m['text'])
            elif m['t'] == 'done':
                return m.get('error')

    def step(self):
        err = self.request('loop')
        self.time += 1 / 30
        return err

    def close(self):
        self.ws.close()


def start_thread(fn, *args, **kwargs):
    t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
