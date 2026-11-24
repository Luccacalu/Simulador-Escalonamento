from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class PriorityReadyProcess(ReadyProcess):
    priority: int

    def __init__(self, process_input: ProcessInput):
        super().__init__(process_input)
        if process_input.priority is None: raise Exception('You must be specify the priority on ProcessInput!')
        self.priority = process_input.priority
