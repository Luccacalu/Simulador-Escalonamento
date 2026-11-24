from dataclasses import dataclass


@dataclass(kw_only=True)
class GlobalMetrics:
    average_turnaround_time: float
    average_waiting_time: float
    average_response_time: float
    lost_deadlines: int
    throughput: float
    idle_time: int
    total_preemptions: int
