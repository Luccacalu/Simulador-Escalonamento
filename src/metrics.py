"""Métricas individuais (tabela final) e globais (resumo)."""
from dataclasses import dataclass

from models import Process, Slot


@dataclass
class IndividualMetric:
    pid: str
    arrival_time: int
    burst_time: int
    deadline: int | None        # instante absoluto (chegada + deadline relativo)
    priority: int | None
    start_time: int
    completion_time: int
    response_time: int          # início - chegada
    turnaround_time: int        # término - chegada  (é o "tempo de resposta")
    waiting_time: int           # turnaround - execução
    deadline_ok: bool | None    # None se o processo não tem deadline


@dataclass
class GlobalMetrics:
    average_turnaround_time: float
    average_waiting_time: float
    average_response_time: float
    lost_deadlines: int
    throughput: float           # processos concluídos por unidade de tempo
    total_time: int
    idle_time: int              # CPU parada esperando chegadas
    overhead_time: int          # tempo gasto em trocas de contexto
    idle_percent: float         # (ociosa + sobrecarga) / total  (o PDF trata sobrecarga como CPU ociosa)
    context_switches: int       # número de trocas de contexto (blocos de sobrecarga)


def individual_metrics(finished: list[Process]) -> list[IndividualMetric]:
    table = []
    for p in sorted(finished, key=lambda p: (p.arrival_time, p.id)):
        turnaround = p.completion_time - p.arrival_time
        dl = p.new_deadline
        table.append(IndividualMetric(
            pid=p.id,
            arrival_time=p.arrival_time,
            burst_time=p.burst_time,
            deadline=dl,
            priority=p.priority,
            start_time=p.start_time,
            completion_time=p.completion_time,
            response_time=p.start_time - p.arrival_time,
            turnaround_time=turnaround,
            waiting_time=turnaround - p.burst_time,
            deadline_ok=None if dl is None else p.completion_time <= dl,
        ))
    return table


def global_metrics(table: list[IndividualMetric], timeline: list[Slot], overhead: int) -> GlobalMetrics:
    n = len(table)
    total = len(timeline)
    idle = sum(1 for s in timeline if s.kind == "idle")
    over = sum(1 for s in timeline if s.kind == "overhead")
    return GlobalMetrics(
        average_turnaround_time=sum(m.turnaround_time for m in table) / n,
        average_waiting_time=sum(m.waiting_time for m in table) / n,
        average_response_time=sum(m.response_time for m in table) / n,
        lost_deadlines=sum(1 for m in table if m.deadline_ok is False),
        throughput=n / total if total else 0.0,
        total_time=total,
        idle_time=idle,
        overhead_time=over,
        idle_percent=100.0 * (idle + over) / total if total else 0.0,
        context_switches=over // overhead if overhead else 0,
    )
