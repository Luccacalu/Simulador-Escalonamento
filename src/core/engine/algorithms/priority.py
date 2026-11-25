from core.process.priority_ready_process import PriorityReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm


class Priority(SchedulingAlgorithm):
    """Prioridades preemptivo (1 = maior prioridade); reavalia a cada fatia."""
    ready_class = PriorityReadyProcess
    needs_quantum = True

    def next(self, on_cpu, ready_queue):
        next = min(self.pending(ready_queue), key=lambda rp: (rp.priority, rp.arrival_time))
        return (next, self.slice_for(next))
