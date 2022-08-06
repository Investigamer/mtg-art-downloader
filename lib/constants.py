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
        """
        Repeatedly check if new print messages have been added and output them.
        """
        while True:
            with LOCK:
                if len(self.out) > 0:
                    msg = self.out.pop(0)
                    print(msg)
                    time.sleep(0.05)
            time.sleep(0.01)

    def flush(self):
        """
        Return only when all messages have flushed.
        """
        while True:
            time.sleep(0.1)
            if len(self.out) == 0:
                time.sleep(0.1)
                return


console = Console()
Thread(target=console.wait, daemon=True).start()
