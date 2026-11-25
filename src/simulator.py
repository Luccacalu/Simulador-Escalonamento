"""Laço de simulação de eventos discretos (CPU single-core, 1 passo = 1 unidade de tempo)."""
from models import Process, Slot
from algorithms import SchedulingAlgorithm


def simulate(inputs: list[Process], alg: SchedulingAlgorithm, overhead: int = 0
             ) -> tuple[list[Slot], list[Process]]:
    """Roda a simulação e devolve (linha do tempo, processos finalizados).

    Os processos recebidos não são modificados (a simulação trabalha em cópias).
    Ordem de entrada na fila de pronto:
      1) ao fim do quantum, chegadas até esse instante entram na fila;
      2) o processo preemptado paga a sobrecarga FORA da fila;
      3) chegadas durante a sobrecarga (inclusive no instante em que ela termina) entram na fila;
      4) só então o processo preemptado volta, para o fim da fila.
    """
    procs = [p.clone() for p in inputs]
    pending = sorted(procs, key=lambda p: p.arrival_time)  # sort estável: respeita a ordem do arquivo
    ready: list[Process] = []
    timeline: list[Slot] = []
    finished: list[Process] = []
    t = 0

    def admit(now: int) -> None:
        while pending and pending[0].arrival_time <= now:
            p = pending.pop(0)
            alg.on_arrival(p, now)
            ready.append(p)

    admit(t)
    while len(finished) < len(procs):
        if not ready:  # CPU ociosa: o tempo avança até a próxima chegada
            timeline.append(Slot(t, "idle", None))
            t += 1
            admit(t)
            continue

        p = alg.pick(ready, t)
        ready.remove(p)
        run = min(alg.slice_for(p), p.remaining_time)
        for _ in range(run):
            if p.start_time is None:
                p.start_time = t
            timeline.append(Slot(t, "exec", p.id))
            p.remaining_time -= 1
            alg.on_run(p, 1)
            t += 1
        admit(t)

        if p.remaining_time == 0:
            p.completion_time = t
            finished.append(p)
            continue

        # não terminou: (talvez) paga a troca de contexto e só então volta para o fim da fila
        pay = False
        if overhead > 0:
            ready.append(p)                      # só para decidir quem seria o próximo
            nxt = alg.pick(ready, t)
            ready.remove(p)
            pay = alg.charge_same or nxt is not p
        if pay:
            for _ in range(overhead):
                timeline.append(Slot(t, "overhead", p.id))
                t += 1
                admit(t)                         # chegadas durante (e no fim da) sobrecarga entram antes de p
        ready.append(p)

    return timeline, finished
