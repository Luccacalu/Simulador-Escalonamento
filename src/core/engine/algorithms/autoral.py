from core.engine.scheduling_algorithm import SchedulingAlgorithm


class Autoral(SchedulingAlgorithm):
    """Autoral: HRRN preemptivo (Highest Response Ratio Next) com fatia de quantum.

    razão = (espera + restante) / restante. Curtos saem logo (como no SJF), mas quem
    espera muito vê a razão crescer (aging) -> sem inanição.
    """
    needs_quantum = True

    def next(self, on_cpu, ready_queue):
        next = max(self.pending(ready_queue),
                   key=lambda rp: ((rp.waiting_time + rp.remaining_time) / rp.remaining_time, -rp.arrival_time))
        return (next, self.slice_for(next))
