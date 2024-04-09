from .common.shared import LogKind, WorkerStatus, WorkerBase

from multiprocessing import Process, Pipe, Lock
from threading import Thread
import os

class ProcessWorker(Process, WorkerBase):
    stop_command = "stop_command"
    pause_command = "pause_command"
    resume_command = "resume_command"
    get_state_command = "get_state_command"

    def __init__(self, auto_start=True, interval:float = 1000, log_size:int = 100) -> None:
        Process.__init__(self)
        WorkerBase.__init__(self, interval, log_size)
        self.server, self.client = Pipe()
        if auto_start:
            self.start()
        self.message_lock = Lock()

    def start(self) -> None:
        self.try_start(lambda: Process.start(self))

    def run(self) -> None:
        self.state.meta["Process Id"] = os.getpid()
        try:
            thread = Thread(target=lambda:self.main_control())
            thread.start()
            while (message := self.server.recv()) != ProcessWorker.stop_command:
                self.server.send(self.main_on_message_handler(message))
            else:
                self.state.status = WorkerStatus.Stopping
                thread.join()
                self.server.send(True)
        except:
            self.log("Fatal failure. Recycle needed", LogKind.Error)
    
    def pause(self):
        self.send_message(ProcessWorker.pause_command)
    
    def resume(self):
        self.send_message(ProcessWorker.resume_command)

    def stop(self, retries: int = 3):
        self.send_message(ProcessWorker.stop_command)

    def get_state(self) -> dict:
        return self.send_message(ProcessWorker.get_state_command)

    def main_on_message_handler(self, message):
        match message:
            case ProcessWorker.pause_command:
                self.set_pause(True)
                return
            case ProcessWorker.resume_command:
                self.set_pause(False)
                return
            case ProcessWorker.get_state_command:
                return self.state.get_snapshot()
            case _:
                return self.on_message(message)

    def on_message(self, message):
        return message
    
    def send_message(self, message):
            with self.message_lock:
                if self.state.status in [WorkerStatus.Stopped, WorkerStatus.Stopping]:
                    return self.main_on_message_handler(message)
                self.client.send(message)
                return self.client.recv()