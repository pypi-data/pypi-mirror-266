from .common.shared import LogKind, WorkerLog, WorkerStatus, WorkerBase

from multiprocessing import Process, Pipe
from threading import Thread, Lock
import os

class ProcessWorker(Process, WorkerBase):
    stop_command = "stop_command"
    pause_command = "pause_command"
    resume_command = "resume_command"
    get_logs_command = "get_logs_command"
    get_status_command = "get_status_command"
    get_meta_command = "get_meta_command"
    get_steps_command = "get_steps_command"

    def __init__(self) -> None:
        Process.__init__(self)
        WorkerBase.__init__(self)
        self.server, self.client = Pipe()
        self.start()
        self.message_lock = Lock()

    def start(self) -> None:
        self.try_start(lambda: Process.start(self))

    def run(self) -> None:
        self.meta["Process Id"] = os.getpid()
        try:
            thread = Thread(target=lambda:self.main_control())
            thread.start()
            while (message := self.server.recv()) != ProcessWorker.stop_command:
                match message:
                    case ProcessWorker.pause_command:
                        self.set_pause(True)
                        self.server.send(None)
                    case ProcessWorker.resume_command:
                        self.set_pause(False)
                        self.server.send(None)
                    case ProcessWorker.get_logs_command:
                        self.server.send(self.logs)
                    case ProcessWorker.get_steps_command:
                        self.server.send([self.current, self.steps, self.step])
                    case ProcessWorker.get_meta_command:
                        self.server.send(self.meta)
                    case ProcessWorker.get_status_command:
                        self.server.send(self.status)
                    case _:
                        self.server.send(self.on_message(message))
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

    def get_logs(self) -> list[WorkerLog]:
        return self.send_message(ProcessWorker.get_logs_command)

    def get_steps(self) -> tuple[str, int, int]:
        return self.send_message(ProcessWorker.get_steps_command)
    
    def get_meta(self) -> dict:
        return self.send_message(ProcessWorker.get_meta_command)
    
    def get_status(self) -> WorkerStatus:
        return self.send_message(ProcessWorker.get_status_command)

    def on_message(self, message):
        return message
    
    def send_message(self, message):
        self.message_lock.acquire()
        try:
            self.client.send(message)
            return self.client.recv()
        finally:
            self.message_lock.release()