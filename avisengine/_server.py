"""
Serve a driver script to the AVIS Sandbox in the browser.

The Sandbox connects to ws://127.0.0.1:<port> from the AVIS Academy page and sends the pairing
code printed here. Only the Academy's own pages may connect (Origin check), only with the code,
and only one browser at a time. Every Run in the browser loads the script again, so edits on the
laptop apply on the next Run.

Per run:  browser {"t": "setup"}  -> laptop runs setup(), answers {"t": "done"} or {"t": "done", "error"}
          browser {"t": "loop"}   -> laptop runs loop() (calling the car through _link), answers the same
          browser {"t": "stop"}   -> the run ends
"""
import contextlib
import io
import json
import os
import queue
import runpy
import secrets
import socket
import sys
import threading
import traceback

from . import _link

DEFAULT_PORT = 8765
ORIGINS = [
    'https://academy.avisengine.com',
    'https://avis-academy.vercel.app',
    'http://localhost:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:5174',
]
PROTOCOL = 1


class _Tee(io.TextIOBase):
    """print() goes to this terminal and to the Sandbox console."""

    def __init__(self, out):
        self.out = out
        self.buf = []

    def write(self, s):
        self.out.write(s)
        self.buf.append(s)
        return len(s)

    def flush(self):
        self.out.flush()

    def take(self):
        text = ''.join(self.buf)
        self.buf = []
        return text


def new_code():
    return f'{secrets.randbelow(1_000_000):06d}'


def nodelay(ws):
    """Small messages go out at once (no Nagle delay): each car call is a round trip."""
    try:
        ws.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (AttributeError, OSError):
        pass


def handshake(ws, code, name):
    """Check the browser's pairing code; True when it may drive."""
    hello = json.loads(ws.recv(timeout=15))
    if hello.get('t') != 'hello' or str(hello.get('code', '')).strip() != code:
        ws.send(json.dumps({'t': 'denied', 'reason': 'Wrong pairing code. Check the code in your terminal.'}))
        return False
    ws.send(json.dumps({'t': 'welcome', 'protocol': PROTOCOL, 'script': name, 'python': sys.version.split()[0]}))
    return True


def ws_serve():
    try:
        from websockets.sync.server import serve
    except ImportError:
        sys.exit('avisengine needs the websockets package: pip install "websockets>=13"')
    return serve


def _user_traceback(path):
    """The traceback without avisengine's own frames."""
    etype, value, tb = sys.exc_info()
    frames = [f for f in traceback.extract_tb(tb) if os.path.abspath(f.filename) == path or 'avisengine' not in f.filename]
    lines = ['Traceback (most recent call last):\n'] + traceback.format_list(frames) + traceback.format_exception_only(etype, value)
    return ''.join(lines).rstrip()


def serve(path, port=DEFAULT_PORT, extra_origins=(), code=None):
    serve_ws = ws_serve()
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        sys.exit(f'No such script: {path}')
    code = code or new_code()
    busy = threading.Lock()
    # setup() and loop() run on the thread that called serve() (the main thread), not on the
    # connection's thread: GUI libraries such as OpenCV's cv2.imshow only work there on macOS.
    jobs = queue.Queue()

    def on_main(fn):
        done = threading.Event()
        box = {}

        def job():
            try:
                box['value'] = fn()
            except BaseException as e:  # handed back to the connection thread
                box['error'] = e
            finally:
                done.set()

        jobs.put(job)
        done.wait()
        if 'error' in box:
            raise box['error']
        return box.get('value')

    def load():
        """A fresh copy of the script: its setup() and loop()."""
        sys.path.insert(0, os.path.dirname(path))
        try:
            return runpy.run_path(path, run_name='__avis__')
        finally:
            sys.path.pop(0)

    def handler(ws):
        nodelay(ws)
        if not busy.acquire(blocking=False):
            ws.send(json.dumps({'t': 'denied', 'reason': 'Another Sandbox tab is already connected.'}))
            return
        try:
            if not handshake(ws, code, os.path.basename(path)):
                return
            print(f'Connected to the AVIS Sandbox. Press Run in the browser to drive with {os.path.basename(path)}.')
            _link.attach(ws)
            ns = None
            tee = _Tee(sys.stdout)
            for raw in ws:
                if isinstance(raw, bytes):
                    continue
                msg = json.loads(raw)
                kind = msg.get('t')
                if kind == 'stop':
                    ns = None
                    continue
                if kind not in ('setup', 'loop'):
                    continue
                state = {'ns': ns, 'error': None}

                def step():
                    with contextlib.redirect_stdout(tee):
                        if kind == 'setup':
                            state['ns'] = load()
                            if not callable(state['ns'].get('loop')):
                                state['error'] = 'Your script needs a loop() function. The Sandbox calls it at the control rate.'
                            elif callable(state['ns'].get('setup')):
                                state['ns']['setup']()
                            if not state['error']:
                                print(f'Running {os.path.basename(path)}.', file=sys.__stdout__)
                        elif state['ns'] is None:
                            state['error'] = 'Press Run in the Sandbox to start the script.'
                        else:
                            state['ns']['loop']()

                error = None
                try:
                    on_main(step)
                    ns, error = state['ns'], state['error']
                except _link.Stopped:
                    ns = None
                    continue
                except Exception:
                    error = _user_traceback(path)
                    print(error, file=sys.stderr)
                    ns = None
                text = tee.take()
                if text:
                    ws.send(json.dumps({'t': 'print', 'text': text}))
                ws.send(json.dumps({'t': 'done', 'error': error} if error else {'t': 'done'}))
        except Exception as e:  # connection closed or bad message
            if type(e).__name__ not in ('ConnectionClosedOK', 'ConnectionClosedError', 'ConnectionClosed'):
                print(f'Connection error: {e}', file=sys.stderr)
        finally:
            _link.attach(None)
            busy.release()
            print('Sandbox disconnected. Waiting for it to connect again.')

    origins = ORIGINS + list(extra_origins)
    with serve_ws(handler, '127.0.0.1', port, origins=origins, max_size=2**24, compression=None) as server:
        print(f'AVIS Engine: serving {os.path.basename(path)} on ws://127.0.0.1:{port}')
        print(f'Pairing code: {code}')
        print('In the AVIS Sandbox, open "Laptop Python", enter the port and this code, then Connect. Ctrl+C to quit.')
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            while True:
                try:
                    job = jobs.get(timeout=0.2)
                except queue.Empty:
                    continue
                job()
        except KeyboardInterrupt:
            print('\nStopped.')
        finally:
            server.shutdown()
