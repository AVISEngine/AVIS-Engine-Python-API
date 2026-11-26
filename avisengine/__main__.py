"""python -m avisengine my_driver.py [--port 8765]"""
import argparse

from ._server import DEFAULT_PORT, serve


def main():
    p = argparse.ArgumentParser(prog='python -m avisengine', description='Drive the AVIS Sandbox in your browser with a Python script on this computer.')
    p.add_argument('script', help='your driver script, with setup() and loop()')
    p.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'local port (default {DEFAULT_PORT})')
    p.add_argument('--origin', action='append', default=[], help='also allow this page origin (for a self-hosted Sandbox)')
    a = p.parse_args()
    serve(a.script, a.port, a.origin)


if __name__ == '__main__':
    main()
