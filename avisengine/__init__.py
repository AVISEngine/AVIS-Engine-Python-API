"""
AVIS Engine Python API.

Two ways to drive:

1. The AVIS Engine desktop simulator, or the web Sandbox, with a classic loop:

    import avisengine
    car = avisengine.Car()
    car.connect("127.0.0.1", 25001)     # desktop simulator
    # car.connectSandbox()              # or the Sandbox in your browser
    while True:
        car.setSpeed(20)
        car.getData()
        image = car.getImage()

2. The web Sandbox with the same setup() / loop() code as its editor
   (python -m avisengine my_driver.py):

    from avisengine import car

    def setup():
        car.setSpeed(30)

    def loop():
        img = car.getImage()
"""

from ._api import IMAGE_HEIGHT, IMAGE_WIDTH, SEMANTIC_CLASSES, car, imshow
from ._link import Stopped
from .avisengine import Car

__version__ = "0.2.0"
__author__ = "Amirmohammad Zarif"
__email__ = "amirmohammadzarif@avisengine.com"

__all__ = ["Car", "car", "imshow", "run", "SEMANTIC_CLASSES", "IMAGE_WIDTH", "IMAGE_HEIGHT", "Stopped"]


def run(port=None):
    """Serve the script that called this to the web Sandbox (same as python -m avisengine <script>).
    Put it under `if __name__ == "__main__":`; each Run in the browser loads the script again."""
    import __main__

    from ._server import DEFAULT_PORT, serve

    path = getattr(__main__, "__file__", None)
    if not path:
        raise RuntimeError("avisengine.run() needs to be called from a script file.")
    serve(path, port or DEFAULT_PORT)
