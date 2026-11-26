from dataclasses import dataclass

from core.process.ready_process import ReadyProcess

@dataclass(kw_only=True)
class Metrics:
    id: int
    arrival_time: int
    burst_time: int
    remaining_time: int
    waiting_time: int
    response_time: int
    completion_time: int
    turnaround_time: int

def check_metrics(rp: ReadyProcess, expected: Metrics):
    return (
        rp.id == expected.id and
        rp.arrival_time == expected.arrival_time and
        rp.burst_time == expected.burst_time and
        rp.remaining_time == expected.remaining_time and
        rp.waiting_time == expected.waiting_time and
        rp.response_time == expected.response_time and
        rp.completion_time == expected.completion_time and
        rp.turnaround_time == expected.turnaround_time
    )
