from .common.shared import LogKind, WorkerLog, WorkerStatus, WorkerBase

from threading import Thread

class ThreadWorker(Thread, WorkerBase):
    def __init__(self, interval:float = 1000, log_size:int = 100) -> None:
        Thread.__init__(self)
        WorkerBase.__init__(self, interval, log_size)

    def start(self) -> None:
        self.try_start(lambda: Thread.start(self))

    def run(self) -> None:
        self.main_control()

    def stop(self, retries:int = 3) -> Thread:
        def stop_thread(self:"ThreadWorker", retries:int):
            if self.status in [WorkerStatus.Stopped, WorkerStatus.Stopping]:
                return
            self.log("Stop requested", LogKind.Information)
            self.status = WorkerStatus.Stopping
            while self.is_alive() and retries > 0:
                self.join(1000)
                retries -= 1
            if self.is_alive():
                self.log("Failed stop", LogKind.Error)
                self.status = WorkerStatus.Active
            else:
                self.log("Success stop", LogKind.Success)
                self.status = WorkerStatus.Stopped
        result:Thread = Thread(target=lambda: stop_thread(self, retries))
        result.start()
        return result
    
    def get_logs(self) -> list[WorkerLog]:
        return self.logs
    
    def get_meta(self) -> dict:
        return self.meta
    
    def get_status(self) -> WorkerStatus:
        return self.status
    
    def get_steps(self) -> tuple[str, int, int]:
        return [self.current, self.steps, self.step]