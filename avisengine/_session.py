"""
The web Sandbox for classic scripts: `car.connectSandbox()` and a `while True:` loop.

The Sandbox connects to this computer (ws://127.0.0.1:<port>) with the printed pairing code.
Each `car.getData()` is one control step: it ends the previous step and waits for the next one,
so the simulator runs in lock-step with the script, as with `setup()` / `loop()` scripts.
If the browser tab closes, `getData()` waits for it to connect again.
"""
import json
import queue
import sys
import threading

from . import _link
from ._server import DEFAULT_PORT, ORIGINS, handshake, new_code, nodelay, ws_serve

_CLOSED = ('ConnectionClosed', 'ConnectionClosedOK', 'ConnectionClosedError')


class SandboxSession:
    def __init__(self, port=DEFAULT_PORT, name='script', extra_origins=(), code=None):
        self.port = port
        self.name = name
        self.code = code or new_code()
        self._new = queue.Queue()
        self._ws = None
        self._release = None
        self._in_step = False
        serve = ws_serve()
        self._server = serve(self._handler, '127.0.0.1', port, origins=ORIGINS + list(extra_origins), max_size=2**24, compression=None)
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        print(f'AVIS Engine: waiting for the AVIS Sandbox on ws://127.0.0.1:{port}')
        print(f'Pairing code: {self.code}')
        print('In the AVIS Sandbox, open "Laptop Python", enter the port and this code, then Connect and Run.')

    def _handler(self, ws):
        nodelay(ws)
        if self._ws is not None:
            ws.send(json.dumps({'t': 'denied', 'reason': 'Another Sandbox tab is already connected.'}))
            return
        if not handshake(ws, self.code, self.name):
            return
        release = threading.Event()
        self._new.put((ws, release))
        release.wait()  # keep the connection open while the script uses it

    def _take(self):
        """Wait for a browser to connect."""
        ws, release = self._new.get()
        self._ws, self._release = ws, release
        self._in_step = False
        _link.attach(ws)
        print('Connected to the AVIS Sandbox. Press Run in the browser.')

    def _drop(self):
        if self._release:
            self._release.set()
        self._ws = self._release = None
        _link.attach(None)

    def wait_connected(self):
        if self._ws is None:
            self._take()

    def next_step(self):
        """End the current control step (if any) and wait for the next one."""
        while True:
            if self._ws is None:
                self._take()
            try:
                if self._in_step:
                    self._in_step = False
                    self._ws.send(json.dumps({'t': 'done'}))
                while True:
                    raw = self._ws.recv()
                    if isinstance(raw, bytes):
                        continue
                    kind = json.loads(raw).get('t')
                    if kind == 'setup':
                        print(f'Running {self.name} in the Sandbox.')
                        self._ws.send(json.dumps({'t': 'done'}))
                    elif kind == 'loop':
                        self._in_step = True
                        return
            except Exception as e:
                if type(e).__name__ not in _CLOSED:
                    raise
                print('Sandbox disconnected. Waiting for it to connect again.', file=sys.stderr)
                self._drop()

    def close(self):
        if self._ws is not None and self._in_step:
            try:
                self._ws.send(json.dumps({'t': 'done'}))
            except Exception:
                pass
        self._drop()
        self._server.shutdown()
