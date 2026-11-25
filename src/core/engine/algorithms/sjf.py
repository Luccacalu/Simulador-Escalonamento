from core.process.ready_process import ReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm


class SJF(SchedulingAlgorithm):
    """Menor job primeiro, não preemptivo (executa até terminar)."""

    def next(self, on_cpu, ready_queue: list[ReadyProcess]) -> tuple[ReadyProcess, int]:
        next = min(self.pending(ready_queue), key=lambda rp: (rp.burst_time, rp.arrival_time))
        return (next, next.burst_time)
