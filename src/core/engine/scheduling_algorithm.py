from abc import ABC, abstractmethod
from core.process.ready_process import ReadyProcess


class SchedulingAlgorithm(ABC):
    ready_class: type[ReadyProcess] = ReadyProcess  # tipo de ReadyProcess que o ProcessExecutor instancia
    needs_quantum: bool = False

    def __init__(self, quantum: int | None = None, overload: int | None = None, seed: int | None = None) -> None:
        if self.needs_quantum and (quantum is None or quantum <= 0):
            raise ValueError(f'{type(self).__name__} exige quantum > 0')
        self.quantum = quantum
        self.overload = overload  # sobrecarga de troca de contexto (u.t.)
        self.seed = seed

    @staticmethod
    def pending(ready_queue: list[ReadyProcess]) -> list[ReadyProcess]:
        return [rp for rp in ready_queue if rp.completion_time is None]

    def slice_for(self, rp: ReadyProcess) -> int:
        return rp.remaining_time if self.quantum is None else min(self.quantum, rp.remaining_time)

    @abstractmethod
    def next(self, on_cpu: None | ReadyProcess | tuple[ReadyProcess, ReadyProcess], ready_queue: list[ReadyProcess]) -> tuple[ReadyProcess, int]:
        """Devolve (próximo processo, fatia em u.t.). `on_cpu` é o último que executou."""
        pass
