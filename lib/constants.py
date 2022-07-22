"""
GLOBAL CONSTANTS
"""
import time
from threading import Thread


class Console:
    def __init__(self):
        self.out = []

    def wait(self):
        while True:
            if len(self.out) > 1:
                msg = self.out.pop()
                print(msg)
            else: time.sleep(.01)

console = Console()
Thread(target=console.wait, daemon=True).start()