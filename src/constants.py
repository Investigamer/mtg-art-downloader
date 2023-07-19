"""
GLOBAL CONSTANTS
"""
import time
from dataclasses import dataclass
from threading import Thread, Lock


@dataclass
class Constants:
    promo_sets = [
        "pre",
        "pmo",
        "dci",
        "fnm",
        # TODO: Investigate: 30a and p30a are really weird
        "pst",
        "30a",
        "slc",
    ]


class Console:
    def __init__(self):
        self.out = []
        self.waiting = True
        self.lock = Lock()

    def wait(self):
        """
        Repeatedly check if new print messages have been added and output them.
        """
        while self.waiting:
            with self.lock:
                if len(self.out) > 0:
                    msg = self.out.pop(0)
                    print(msg)
                    print("", end="", flush=True)
                    time.sleep(0.05)
                time.sleep(0.01)

    def flush(self):
        """
        Return only when all messages have flushed.
        """
        while True:
            time.sleep(0.1)
            with self.lock:
                if len(self.out) == 0:
                    time.sleep(0.1)
                    self.waiting = False
                    return

    def print(self, message: str):
        """
        Add a message to the output queue.
        @param message: Message to add to the queue.
        """
        with self.lock:
            self.out.append(message)


con = Constants
console = Console()
Thread(target=console.wait, daemon=True).start()
