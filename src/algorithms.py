"""Algoritmos de escalonamento.

Cada algoritmo decide duas coisas:
    - pick(ready, t): qual processo da fila de prontos executa agora (função pura, sem efeitos);
    - slice_for(p):   por quantas unidades de tempo ele executa antes de a CPU reavaliar.

Regras de sobrecarga:
    - não preemptivos (FCFS, SJF): rodam até o fim, sem sobrecarga;
    - preemptivos com quantum (RR, Priority, EDF, AGING): ao fim de cada quantum, se o processo
    não terminou, paga-se a sobrecarga, mesmo que o mesmo processo continue (charge_same=True);
    - CFS: fatia curta (granularidade); só paga sobrecarga ao trocar de processo (charge_same=False).
    - quando um processo termina, ou no primeiro despacho, não há sobrecarga.
"""
from models import Process


class SchedulingAlgorithm:
    name = "BASE"
    preemptive = False
    charge_same = True  # cobra sobrecarga ao fim do quantum mesmo se o próximo for o mesmo processo

    def __init__(self, quantum: int = 2) -> None:
        self.quantum = quantum

    def pick(self, ready: list[Process], t: int) -> Process:
        raise NotImplementedError

    def slice_for(self, p: Process) -> int:
        return self.quantum if self.preemptive else p.remaining_time

    # chamado quando um processo entra na fila de prontos pela primeira vez (CFS usa)
    def on_arrival(self, p: Process, t: int) -> None:
        pass

    # chamado depois de cada unidade executada (CFS usa)
    def on_run(self, p: Process, units: int) -> None:
        pass


def _first_min(ready: list[Process], key) -> Process:
    # min() devolve o primeiro mínimo: empates são resolvidos pela ordem da fila (estável)
    return min(ready, key=key)


class FCFS(SchedulingAlgorithm):
    name = "FCFS"

    def pick(self, ready, t):
        return _first_min(ready, lambda p: p.arrival_time)


class SJF(SchedulingAlgorithm):
    """Não preemptivo: entre os prontos, o menor tempo de execução total."""
    name = "SJF"

    def pick(self, ready, t):
        return _first_min(ready, lambda p: (p.burst_time, p.arrival_time))


class RoundRobin(SchedulingAlgorithm):
    """Fila circular: o primeiro da fila executa um quantum e volta para o fim."""
    name = "RR"
    preemptive = True

    def pick(self, ready, t):
        return ready[0]


class Priority(SchedulingAlgorithm):
    """Prioridade preemptiva (1 = maior prioridade). Reavalia a cada quantum."""
    name = "PRIORITY"
    preemptive = True

    def pick(self, ready, t):
        for p in ready:
            if p.priority is None:
                raise ValueError(f"Processo {p.id} sem prioridade (obrigatória no algoritmo PRIORITY)")
        return _first_min(ready, lambda p: (p.priority, p.arrival_time))


class EDF(SchedulingAlgorithm):
    """Earliest Deadline First: menor deadline absoluto (chegada + deadline). Reavalia a cada quantum."""
    name = "EDF"
    preemptive = True

    def pick(self, ready, t):
        for p in ready:
            if p.deadline is None:
                raise ValueError(f"Processo {p.id} sem deadline (obrigatório no algoritmo EDF)")
        return _first_min(ready, lambda p: (p.new_deadline, p.arrival_time))


class CFS(SchedulingAlgorithm):
    """CFS-Sim: menor vruntime executa; vruntime += Δt * 1.25^(prioridade-1).

    - ao chegar: vruntime = tempo atual;
    - fatia = `granularity` (1 u.t.), então a preempção acontece assim que outro processo
      tem vruntime menor (a fatia efetiva "emerge" do reequilíbrio);
    - sobrecarga só quando troca de processo.
    """
    name = "CFS"
    preemptive = True
    charge_same = False

    def __init__(self, quantum: int = 2, granularity: int = 1) -> None:
        super().__init__(quantum)
        self.granularity = granularity

    @staticmethod
    def weight(priority: int | None) -> float:
        return 1.25 ** ((priority if priority is not None else 1) - 1)

    def slice_for(self, p):
        return self.granularity

    def on_arrival(self, p, t):
        p.vruntime = float(t)

    def on_run(self, p, units):
        p.vruntime += units * self.weight(p.priority)

    def pick(self, ready, t):
        return _first_min(ready, lambda p: (p.vruntime, p.arrival_time))


class Aging(SchedulingAlgorithm):
    """Algoritmo autoral: SRTF com envelhecimento (aging).

    Pontuação = tempo restante - 0.5 * tempo que o processo já passou sem executar.
    Vence a menor pontuação. Favorece jobs curtos (bom turnaround médio, como SRTF), mas quem
    espera muito vai "ficando mais curto" na pontuação, o que evita inanição de jobs longos.
    Reavalia a cada quantum.
    """
    name = "AGING"
    preemptive = True
    AGING_FACTOR = 0.5

    def pick(self, ready, t):
        def score(p: Process):
            executed = p.burst_time - p.remaining_time
            waited = (t - p.arrival_time) - executed
            return (p.remaining_time - self.AGING_FACTOR * waited, p.arrival_time)
        return _first_min(ready, score)


ALGORITHMS = {
    "FCFS": FCFS,
    "SJF": SJF,
    "RR": RoundRobin,
    "PRIORITY": Priority,
    "EDF": EDF,
    "CFS": CFS,
    "AGING": Aging,
}


def make_algorithm(name: str, quantum: int = 2) -> SchedulingAlgorithm:
    key = name.upper()
    if key not in ALGORITHMS:
        raise ValueError(f"Algoritmo desconhecido: {name}. Opções: {', '.join(ALGORITHMS)}")
    return ALGORITHMS[key](quantum=quantum)
