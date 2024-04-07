from .common.shared import LogKind, WorkerStatus, WorkerBase

from multiprocessing import Process, Pipe
from threading import Thread, Lock
import os

class ProcessWorker(Process, WorkerBase):
    stop_command = "stop_command"
    pause_command = "pause_command"
    resume_command = "resume_command"
    get_state_command = "get_state_command"

    def __init__(self) -> None:
        Process.__init__(self)
        WorkerBase.__init__(self)
        self.server, self.client = Pipe()
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
                self.status = WorkerStatus.Stopping
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
        if self.message_lock.acquire(timeout=0.2):
            try:
                if self.state.status == WorkerStatus.Stopped:
                    return self.main_on_message_handler(message)
                self.client.send(message)
                return self.client.recv()
            finally:
                self.message_lock.release()