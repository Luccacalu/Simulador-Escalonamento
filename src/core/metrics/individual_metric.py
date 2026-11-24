from core.process.deadline_ready_process import DeadlineReadyProcess
from core.process.priority_ready_process import PriorityReadyProcess
from core.process.ready_process import ReadyProcess


type GenericReadyProcess = ReadyProcess | DeadlineReadyProcess | PriorityReadyProcess

class IndividualMetric:
    pid: int
    arrival_time: int
    burst_time: int
    response_time: int
    waiting_time: int
    completion_time: int
    turnaround_time: int
    priority: int | None
    deadline: int | None
    deadline_ok: bool | None

    def __init__(self, ready_process: GenericReadyProcess):
        self.pid = ready_process.id
        self.arrival_time = ready_process.arrival_time
        self.burst_time = ready_process.burst_time

        self.waiting_time = ready_process.waiting_time

        if ready_process.response_time is None: raise Exception()
        self.response_time = ready_process.response_time

        if ready_process.completion_time is None: raise Exception()
        self.completion_time = ready_process.completion_time

        if ready_process.turnaround_time is None: raise Exception()
        self.turnaround_time = ready_process.turnaround_time

        self.priority = getattr(ready_process, 'priority', None)
        self.deadline = getattr(ready_process, 'deadline', None)
        self.deadline_ok = getattr(ready_process, 'deadline_ok', None)
