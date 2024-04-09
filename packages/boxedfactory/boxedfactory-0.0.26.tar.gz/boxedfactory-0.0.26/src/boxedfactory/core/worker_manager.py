from .common.shared import WorkerBase
from .common.cryptography import newid
from typing import Callable

WorkerFactory = dict[str, Callable[[], WorkerBase]]
WorkerPool = dict[str, dict[str, WorkerBase]]

class WorkerManager:
    def __init__(self, factory:WorkerFactory) -> None:
        self.factory:WorkerFactory = factory
        self.pool:WorkerPool = {i:dict() for i in self.factory}

    def create(self, kind:str, id:str = None) -> str:
        id = id or newid()
        if kind in self.factory:
            if id in self.pool[kind]:
                self.recycle(kind, id)
            else:
                self.pool[kind][id] = self.factory[kind]()
            return id
        else:
            raise Exception(f"Worker type {kind} not found")
        
    def get_worker(self, kind:str, id:str) -> WorkerBase:
        if kind in self.pool:
            if id in self.pool[kind]:
                return self.pool[kind][id]
            else:
                raise Exception(f"Worker type {kind} with id {id} not found")
        else:
            raise Exception(f"Worker type {kind} not found")
        
    def get_types(self) -> list[str]:
        return [i for i in self.factory]
    
    def get_worker_ids(self, kind:str) -> list[str]:
        if kind in self.pool:
            return [i for i in self.pool[kind]]
        else:
            raise Exception(f"Worker type {kind} not found")
        
    def recycle(self, kind:str, id:str) -> str:
        self.remove(kind, id)
        print(f'recycle: {id}')
        self.pool[kind][id] = self.factory[kind]()
        return id
    
    def remove(self, kind:str, id:str) -> str:
        w = self.get_worker(kind, id)
        print(f'remove: {id}')
        w.stop()
        del self.pool[kind][id]
        return id
    
    def __del__(self):
        for kind in self.pool:
            kind_ids = [i for i in self.pool[kind]]
            for id in kind_ids:
                self.remove(kind, id)