from core.process.deadline_ready_process import DeadlineReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm


class EDF(SchedulingAlgorithm):
    """Earliest Deadline First preemptivo; reavalia a cada fatia."""
    ready_class = DeadlineReadyProcess
    needs_quantum = True

    def next(self, on_cpu, ready_queue):
        next = min(self.pending(ready_queue), key=lambda rp: (rp.new_deadline, rp.arrival_time))
        return (next, self.slice_for(next))
