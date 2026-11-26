from core.process.ready_process import ReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm

class FCFS(SchedulingAlgorithm):
    def __init__(self, quantum: int | None = None, overload: int | None = None, seed: int | None = None) -> None:
        super().__init__(quantum, overload, seed)

    def next(self, on_cpu: None | ReadyProcess | tuple[ReadyProcess, ReadyProcess], ready_queue: list[ReadyProcess]) -> tuple[ReadyProcess, int]:
        next: ReadyProcess | None = None
        for rp in ready_queue:
            if (rp.completion_time is not None):
                continue

            if (next is None):
                next = rp
                continue

            if (rp.arrival_time < next.arrival_time):
                next = rp

        if (next is None): raise Exception('Couldn\'t find the next process')

        return (next, next.burst_time)
