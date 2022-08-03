"""
GLOBAL CONSTANTS
"""
import time
from threading import Thread, Lock

LOCK = Lock()


class Console:
    def __init__(self):
        self.out = []

    def wait(self):
        while True:
            with LOCK:
                if len(self.out) > 1:
                    msg = self.out.pop()
                    print(msg)
                    time.sleep(0.05)
            time.sleep(0.01)


console = Console()
Thread(target=console.wait, daemon=True).start()
