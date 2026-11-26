'''
@ 2025, Copyright AVIS Engine
- Drive the AVIS Sandbox in your browser (academy.avisengine.com) from this computer.

    python -m avisengine example_sandbox.py

The command prints a port and a pairing code. In the Sandbox, open "Laptop Python", enter them,
press Connect, then Run. This is the same setup() / loop() code as the Sandbox's own editor.
Each Run loads this file again, so edits apply on the next Run.
'''
import cv2
import numpy as np

from avisengine import car

KP = 0.4  # steering gain: percent of full lock per pixel of error


def setup():
    car.setSpeed(30)
    print("Control rate:", car.getControlRate(), "Hz")


def loop():
    img = car.getImage()                       # (120, 160, 3) BGR, like OpenCV
    white = (img > 160).all(axis=2)            # lane paint: bright in every channel
    ys, xs = np.nonzero(white[80:])            # look at the road just ahead
    if len(xs):
        error = xs.mean() - 80                 # pixels right of the image center
        car.setSteering(float(np.clip(KP * error, -100, 100)))

    # Your own OpenCV windows work here too.
    cv2.imshow("camera", img)
    cv2.waitKey(1)
