from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class DeadlineReadyProcess(ReadyProcess):
    new_deadline: int
    deadline_ok: bool = False

    def __init__(self, process_input: ProcessInput):
        super().__init__(process_input)
        if process_input.deadline is None:
            raise ValueError('EDF exige deadline em todos os processos')

        self.new_deadline = process_input.deadline + process_input.arrival_time
