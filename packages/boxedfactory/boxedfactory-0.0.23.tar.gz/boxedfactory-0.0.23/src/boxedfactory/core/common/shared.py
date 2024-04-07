import time
from enum import IntEnum
from typing import Callable

class LogKind:
    Information = "Information"
    Alert = "Alert"
    Error = "Error"
    Warning = "Warning"
    Success = "Success"

class WorkerLog:
    def __init__(self, title:str, kind:LogKind = LogKind.Information, detail:str = None) -> None:
        self.epoch:float = time.time()
        self.kind = kind
        self.title = title
        self.detail = detail or ''

class WorkerStatus(IntEnum):
    Stopped = 1
    Stopping = 2
    Paused = 3
    Active = 4

class OperationState():
    def __init__(self, log_size:int = 100) -> None:       
        self.log_size = log_size
        self.status:WorkerStatus = WorkerStatus.Stopped
        self.logs:list[WorkerLog] = []
        self.current:str = ''
        self.steps = 0
        self.step = 0
        self.meta:dict = dict()

    def log(self, title, kind:LogKind = LogKind.Information, detail:str = None):
        while len(self.logs) > self.log_size:
            self.logs.pop()
        self.logs.append(WorkerLog(title, kind, detail))

    def get_snapshot(self):
        return self.__dict__

class WorkerBase:
    def __init__(self, interval:float = 1000, log_size:int = 100) -> None:
        self.state = OperationState(log_size)
        self.interval = self.set_interval(interval)

    def try_start(self, on_start:Callable[[],None]):
        if self.state.status == WorkerStatus.Stopped:
            self.state.status = WorkerStatus.Active
            self.state.log("Started", LogKind.Success)
            return on_start()

    def set_interval(self, interval:float):
        self.interval = max(10, min(0.1, interval))
        return self.interval

    def main_control(self):
        while self.state.status not in [WorkerStatus.Stopped, WorkerStatus.Stopping]:
            if self.state.status != WorkerStatus.Paused:
                self.main_event_loop()
            time.sleep(self.interval)
        self.state.status = WorkerStatus.Stopped

    def set_pause(self, paused:bool = True):
        if paused and self.state.status != WorkerStatus.Paused:
            self.state.status = WorkerStatus.Paused
            self.state.log("Paused", LogKind.Success)
        elif not paused and self.state.status == WorkerStatus.Paused:
            self.state.status = WorkerStatus.Active
            self.state.log("Resumed", LogKind.Success)

    def pause(self):
        return self.set_pause(True)

    def resume(self):
        return self.set_pause(False)

    def stop(self, retries:int = 3):
        raise NotImplemented()
    
    def start(self):
        raise NotImplemented()
    
    def run(self):
        raise NotImplemented()
    
    def get_state(self) -> dict:
        raise NotImplemented()

    def main_event_loop(self):
        raise NotImplemented()