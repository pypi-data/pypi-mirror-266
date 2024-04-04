import time
import random
from .thread_worker import Worker, LogKind

class TestWorker(Worker):
    def __init__(self, interval: float = 1, log_size: int = 100) -> None:
        super().__init__(interval, log_size)

    def main_event_loop(self):
        time.sleep(10 * random.random())
        self.log("On step", LogKind.Success, "Ready")