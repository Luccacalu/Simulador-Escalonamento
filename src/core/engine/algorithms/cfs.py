from core.process.fair_ready_process import FairReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm


class CFS(SchedulingAlgorithm):
    """CFS-Sim: executa o processo de MENOR vruntime por uma fatia granular (Δt = quantum).

    vruntime += Δt * 1.25^(prioridade-1) (feito no FairReadyProcess). A preempção
    acontece quando, ao fim da fatia, outro processo passou a ter vruntime menor.
    """
    ready_class = FairReadyProcess
    needs_quantum = True

    def next(self, on_cpu, ready_queue):
        next = min(self.pending(ready_queue), key=lambda rp: (rp.vruntime, rp.arrival_time))
        return (next, self.slice_for(next))
