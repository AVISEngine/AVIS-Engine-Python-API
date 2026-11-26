"""The web Sandbox: setup()/loop() scripts and classic Car scripts, against a stand-in Sandbox page."""
import json
import textwrap

import numpy as np
import pytest
from fake_sandbox import FakeSandbox, free_port, start_thread, wait_port
from websockets.sync.client import connect

import avisengine
from avisengine import _server

CODE = '123456'


@pytest.fixture
def loop_script(tmp_path):
    """Serve a setup()/loop() script; yields (port, path)."""

    def make(source):
        path = tmp_path / 'driver.py'
        path.write_text(textwrap.dedent(source))
        port = free_port()
        start_thread(_server.serve, str(path), port, code=CODE)
        wait_port(port)
        return port, path

    return make


def test_exports():
    assert callable(avisengine.Car)
    assert hasattr(avisengine.car, 'getImage')
    assert avisengine.SEMANTIC_CLASSES[0] == 'road'


def test_loop_script_drives_and_reads(loop_script):
    port, _ = loop_script(
        """
        from avisengine import car

        def setup():
            car.setSpeed(30)
            print('ready')

        def loop():
            img = car.getImage()
            b, g, r = img[60, 80]
            car.setSteering(float(r))     # 30: the red value of the test pixel
            print(img.shape, car.getSensors())
        """
    )
    sb = FakeSandbox(port, CODE)
    assert sb.welcome['t'] == 'welcome' and sb.welcome['script'] == 'driver.py'
    assert sb.request('setup') is None
    assert sb.speed_cmd == 30
    assert sb.step() is None
    assert sb.steer_cmd == 30
    assert '(120, 160, 3) [1500, 700, 1500]' in ''.join(sb.prints)
    sb.close()


def test_loop_errors_show_the_users_line(loop_script):
    port, _ = loop_script(
        """
        from avisengine import car

        def loop():
            return car.getImage()[200, 0]
        """
    )
    sb = FakeSandbox(port, CODE)
    assert sb.request('setup') is None
    err = sb.step()
    assert 'IndexError' in err and 'driver.py' in err and 'avisengine/_' not in err
    sb.close()


def test_each_run_loads_the_script_again(loop_script):
    port, path = loop_script("def loop():\n    print('v1')\n")
    sb = FakeSandbox(port, CODE)
    sb.request('setup')
    sb.step()
    path.write_text("def loop():\n    print('v2')\n")
    sb.request('setup')
    sb.step()
    assert sb.prints[-1].strip() == 'v2'
    sb.close()


def test_missing_loop_is_explained(loop_script):
    port, _ = loop_script('x = 1\n')
    sb = FakeSandbox(port, CODE)
    assert 'loop()' in sb.request('setup')
    sb.close()


def test_wrong_code_is_denied(loop_script):
    port, _ = loop_script('def loop():\n    pass\n')
    with connect(f'ws://127.0.0.1:{port}', origin='http://localhost:5174') as ws:
        ws.send(json.dumps({'t': 'hello', 'code': '000000'}))
        assert json.loads(ws.recv(timeout=5))['t'] == 'denied'


def test_other_websites_cannot_connect(loop_script):
    port, _ = loop_script('def loop():\n    pass\n')
    with pytest.raises(Exception):
        connect(f'ws://127.0.0.1:{port}', origin='https://example.com', open_timeout=5)


def test_classic_car_drives_the_sandbox():
    port = free_port()
    seen = {}

    def classic_script():
        car = avisengine.Car()
        car.connectSandbox(port, code=CODE)
        for _ in range(3):
            car.setSpeed(20)
            car.setSteering(-10)
            car.getData()
        seen['image'] = car.getImage()
        seen['sensors'] = car.getSensors()
        seen['speed'] = car.getSpeed()
        car.setSpeed(40)
        car.getData()  # ends the last step
        car.stop()

    t = start_thread(classic_script)
    sb = FakeSandbox(port, CODE)
    assert sb.request('setup') is None
    for _ in range(4):
        assert sb.step() is None
    t.join(timeout=10)
    assert not t.is_alive()
    assert isinstance(seen['image'], np.ndarray) and seen['image'].shape == (120, 160, 3)
    assert list(seen['image'][60, 80]) == [10, 20, 30]  # BGR
    assert seen['sensors'] == [1500, 700, 1500]
    assert seen['speed'] == 7  # 20 percent -> 2.0 m/s in the fake sim -> 7 km/h
    assert ('set_steering', -10.0) in sb.history
    assert ('set_speed', 40.0) in sb.history
    # stop() leaves the car still.
    assert sb.history[-2:] == [('set_speed', 0.0), ('set_steering', 0.0)]


def test_loop_runs_on_the_serving_thread(tmp_path):
    """setup() and loop() run on the thread that called serve() (the main thread for
    python -m avisengine), because GUI calls such as cv2.imshow only work there on macOS."""
    import threading

    path = tmp_path / 'driver.py'
    path.write_text('import threading\ndef loop():\n    print(threading.current_thread().name)\n')
    port = free_port()
    threading.Thread(target=_server.serve, args=(str(path), port), kwargs={'code': CODE}, name='serving-thread', daemon=True).start()
    wait_port(port)
    sb = FakeSandbox(port, CODE)
    sb.request('setup')
    sb.step()
    assert sb.prints[-1].strip() == 'serving-thread'
    sb.close()
