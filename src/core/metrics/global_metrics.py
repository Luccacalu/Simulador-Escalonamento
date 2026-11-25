from dataclasses import dataclass


@dataclass(kw_only=True)
class GlobalMetrics:
    average_turnaround_time: float   # = "tempo médio de resposta"
    average_waiting_time: float
    average_response_time: float     # início - chegada
    lost_deadlines: int
    throughput: float                # processos por u.t.
    idle_time: int
    total_preemptions: int           # = trocas de contexto
    idle_percent: float = 0.0
    overhead_time: int = 0
    overhead_percent: float = 0.0
    total_time: int = 0
