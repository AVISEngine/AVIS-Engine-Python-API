"""The classic desktop protocol, against a stand-in for the AVIS Engine simulator."""
import base64
import socket
import threading

import cv2
import numpy as np
from fake_sandbox import free_port

import avisengine


def fake_simulator(port, ready, received):
    img = np.zeros((40, 60, 3), np.uint8)
    img[10, 20] = (1, 2, 3)
    ok, png = cv2.imencode('.png', img)
    reply = f"<image>{base64.b64encode(png.tobytes()).decode()}</image><sensor>[300,1500,1500]</sensor><speed>12</speed><EOF>".encode()
    with socket.socket() as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('127.0.0.1', port))
        srv.listen(1)
        ready.set()
        conn, _ = srv.accept()
        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                text = data.decode()
                received.append(text)
                if 'ImageStatus:1' in text:
                    conn.sendall(reply)
                if text.endswith('stop'):
                    break


def test_desktop_get_data():
    port = free_port()
    ready, received = threading.Event(), []
    threading.Thread(target=fake_simulator, args=(port, ready, received), daemon=True).start()
    ready.wait(5)
    car = avisengine.Car()
    car.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # a fresh socket per test
    assert car.connect('127.0.0.1', port)
    car.setSpeed(20)
    car.getData()
    assert car.getSensors() == [300, 1500, 1500]
    assert car.getSpeed() == 12
    assert tuple(car.getImage()[10, 20]) == (1, 2, 3)
    car.stop()
    assert any(t.startswith('Speed:20,') for t in received)
