from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class FairReadyProcess(ReadyProcess):
    vruntime: float
    weight: float

    def __init__(self, process_input: ProcessInput):
        super().__init__(process_input)
        nice = process_input.priority if process_input.priority is not None else 1
        self.weight = 1.25 ** (nice - 1)            # w(prioridade)
        self.vruntime = float(self.arrival_time)    # ao chegar, vruntime = tempo_atual

    def execute(self, instant: int):
        if (self.remaining_time == 0): return
        super().execute(instant)
        self.vruntime += 1 * self.weight            # Δt (1 u.t.) * w(prioridade)
