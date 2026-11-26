from core.process.ready_process import ReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm


class RoundRobin(SchedulingAlgorithm):
    """Circular. O algoritmo é dono da sua fila (ordem de atendimento).

    Quem chegou até agora (inclusive durante a sobrecarga) entra ANTES do processo
    preemptado (`on_cpu`), que volta ao fim da fila.
    """
    needs_quantum = True

    def __init__(self, quantum: int | None = None, overload: int | None = None, seed: int | None = None) -> None:
        super().__init__(quantum, overload, seed)
        self._queue: list[ReadyProcess] = []

    def next(self, on_cpu, ready_queue: list[ReadyProcess]) -> tuple[ReadyProcess, int]:
        for rp in self.pending(ready_queue):
            if rp is not on_cpu and rp not in self._queue:
                self._queue.append(rp)
        if isinstance(on_cpu, ReadyProcess) and on_cpu.completion_time is None and on_cpu not in self._queue:
            self._queue.append(on_cpu)

        next = self._queue.pop(0)
        return (next, self.slice_for(next))
