from abc import ABC, abstractmethod
from core.process.ready_process import ReadyProcess


class SchedulingAlgorithm(ABC):
    @abstractmethod
    def next(self, on_cpu: None | ReadyProcess | tuple[ReadyProcess, ReadyProcess], ready_queue: list[ReadyProcess]) -> tuple[ReadyProcess, int]:
        pass
