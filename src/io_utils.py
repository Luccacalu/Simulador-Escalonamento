"""Entrada (JSON) e saída textual (log, tabela, resumo).
"""
import json
from dataclasses import dataclass

from models import Process, Slot
from metrics import IndividualMetric, GlobalMetrics


@dataclass
class Config:
    processes: list[Process]
    quantum: int = 2
    overhead: int = 0
    disk_cost: int = 0   # bônus (memória virtual): lido, mas não usado
    seed: int = 42


def load_input(path: str) -> Config:
    """Lê o JSON no formato recomendado (chegada, execucao, deadline, prioridade, ...)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    procs = []
    for d in data["processos"]:
        procs.append(Process(
            id=str(d["id"]),
            arrival_time=int(d["chegada"]),
            burst_time=int(d["execucao"]),
            deadline=d.get("deadline"),
            priority=d.get("prioridade"),
        ))
    if len({p.id for p in procs}) != len(procs):
        raise ValueError("ids de processo duplicados no JSON")
    return Config(
        processes=procs,
        quantum=int(data.get("quantum", 2)),
        overhead=int(data.get("sobrecarga_contexto", 0)),
        disk_cost=int(data.get("custo_disco", 0)),
        seed=int(data.get("seed", 42)),
    )


def describe_slot(s: Slot) -> str:
    if s.kind == "exec":
        return f"t={s.t}: executando {s.pid}"
    if s.kind == "overhead":
        return f"t={s.t}: troca de contexto (saindo {s.pid})"
    return f"t={s.t}: CPU ociosa"


def format_table(table: list[IndividualMetric]) -> str:
    head = ["proc", "chegada", "exec", "deadline", "prio", "inicio", "termino", "espera", "turnaround", "deadline_ok?"]
    rows = [head]
    for m in table:
        ok = "-" if m.deadline_ok is None else ("sim" if m.deadline_ok else "NAO")
        rows.append([m.pid, m.arrival_time, m.burst_time,
                     "-" if m.deadline is None else m.deadline,
                     "-" if m.priority is None else m.priority,
                     m.start_time, m.completion_time, m.waiting_time, m.turnaround_time, ok])
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(head))]
    return "\n".join("  ".join(str(c).rjust(w) for c, w in zip(r, widths)) for r in rows)


def format_summary(g: GlobalMetrics) -> str:
    return "\n".join([
        f"Turnaround médio : {g.average_turnaround_time:.2f}",
        f"Espera média     : {g.average_waiting_time:.2f}",
        f"Resposta média   : {g.average_response_time:.2f}  (início - chegada)",
        f"Deadlines perdidos: {g.lost_deadlines}",
        f"Throughput       : {g.throughput:.4f} processos/u.t.",
        f"Tempo total      : {g.total_time} u.t.",
        f"CPU ociosa       : {g.idle_percent:.1f}%  (ociosa={g.idle_time} + sobrecarga={g.overhead_time})",
        f"Trocas de contexto: {g.context_switches}",
    ])


def write_log(path: str, alg_name: str, timeline: list[Slot], table: list[IndividualMetric],
              summary: GlobalMetrics) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Algoritmo: {alg_name}\n\n")
        f.write("\n".join(describe_slot(s) for s in timeline))
        f.write("\n\n" + format_table(table) + "\n\n" + format_summary(summary) + "\n")
