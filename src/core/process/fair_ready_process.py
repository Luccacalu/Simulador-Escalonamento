from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class FairReadyProcess(ReadyProcess):
    vruntime: int | None

    def __init__(self, process_input: ProcessInput):
        super().__init__(process_input)
