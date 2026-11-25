from pathlib import Path

import pytest

from algorithms import ALGORITHMS, make_algorithm
from simulator import simulate
from metrics import individual_metrics, global_metrics
from io_utils import load_input
from cli import main

CASOS = Path(__file__).resolve().parents[1] / "casos"


def run(caso: str, alg: str, overhead=None):
    cfg = load_input(str(CASOS / caso))
    ov = cfg.overhead if overhead is None else overhead
    timeline, finished = simulate(cfg.processes, make_algorithm(alg, cfg.quantum), ov)
    table = individual_metrics(finished)
    return timeline, table, global_metrics(table, timeline, ov)


def drawing(timeline):
    """Linha do tempo em texto: letra = executando, s = sobrecarga, . = ociosa."""
    return "".join(s.pid if s.kind == "exec" else ("s" if s.kind == "overhead" else ".") for s in timeline)


# ---------- resolução do professor (A=0/8, B=4/4, C=8/2, D=12/7; quantum 2; sobrecarga 1) ----------
# Obs.: o "tempo médio de resposta" do professor é o turnaround médio (término - chegada).

def test_professor_fifo():
    _, table, g = run("caso_professor.json", "FCFS")
    assert [m.turnaround_time for m in table] == [8, 8, 6, 9]
    assert g.average_turnaround_time == 7.75
    assert g.context_switches == 0  # não preemptivo: sem sobrecarga


def test_professor_sjf():
    _, table, g = run("caso_professor.json", "SJF")
    assert [m.turnaround_time for m in table] == [8, 10, 2, 9]
    assert g.average_turnaround_time == 7.25


def test_professor_edf_todos_cumprem_deadline():
    _, table, g = run("caso_professor.json", "EDF")
    assert [m.turnaround_time for m in table] == [18, 7, 5, 16]
    assert g.average_turnaround_time == 11.5
    assert g.lost_deadlines == 0 and all(m.deadline_ok for m in table)


def test_professor_rr_igual_a_grade_da_folha():
    # grade da folha (s = sobrecarga, na linha de quem saiu): o D vem antes do A depois do B terminar,
    # porque o D chega durante a sobrecarga do A (t=12), antes de o A voltar para a fila.
    timeline, table, g = run("caso_professor.json", "RR")
    assert drawing(timeline) == "AAsAAsBBsAAsCCBBDDsAADDsDDsD"
    assert [m.turnaround_time for m in table] == [21, 12, 6, 16]
    assert g.average_turnaround_time == 13.75


# ---------- teste original do colega (FCFS, 5 processos, sem sobrecarga) ----------

def test_fcfs_cinco_processos():
    _, table, _ = run("caso_fcfs_5.json", "FCFS")
    esperado = {  # pid: (espera, resposta, término, turnaround)
        "P1": (0, 0, 10, 10), "P2": (9, 9, 16, 15), "P3": (14, 14, 18, 16),
        "P4": (15, 15, 22, 19), "P5": (18, 18, 30, 26),
    }
    for m in table:
        assert (m.waiting_time, m.response_time, m.completion_time, m.turnaround_time) == esperado[m.pid]


# ---------- ociosidade ----------

def test_ociosidade_fcfs():
    timeline, table, g = run("caso_ociosidade.json", "FCFS")
    kinds = "".join("i" if s.kind == "idle" else "x" for s in timeline)
    assert kinds == "ii" + "xxx" + "i" * 7 + "xx" + "xxxx"   # P1 em 2-5, P2 em 12-14, P3 em 14-18
    assert g.idle_time == 9           # 0-2 e 5-12
    assert g.total_time == 18
    assert g.idle_percent == 50.0


# ---------- propriedades que valem para TODOS os algoritmos ----------

@pytest.mark.parametrize("alg", list(ALGORITHMS))
@pytest.mark.parametrize("caso", ["caso1.json", "caso_professor.json", "caso_ociosidade.json"])
def test_invariantes(alg, caso):
    timeline, table, g = run(caso, alg)
    # linha do tempo contínua, 1 slot por unidade
    assert [s.t for s in timeline] == list(range(len(timeline)))
    for m in table:
        executado = sum(1 for s in timeline if s.kind == "exec" and s.pid == m.pid)
        assert executado == m.burst_time                      # executou exatamente o burst
        assert m.start_time >= m.arrival_time                 # ninguém executa antes de chegar
        assert m.completion_time - m.arrival_time == m.turnaround_time
        assert m.waiting_time == m.turnaround_time - m.burst_time >= 0
    assert g.total_time == len(timeline)
    # CPU só fica ociosa se realmente não havia ninguém pronto
    chegadas = {m.pid: m.arrival_time for m in table}
    for s in timeline:
        if s.kind == "idle":
            assert all(not (chegadas[m.pid] <= s.t < m.completion_time) for m in table)


# ---------- regras específicas ----------

def test_prioridade_menor_numero_vence():
    timeline, table, _ = run("caso_professor.json", "PRIORITY")
    # B (prio 1) deve terminar antes de A (prio 3) e D (prio 4) quando disputam a CPU
    comp = {m.pid: m.completion_time for m in table}
    assert comp["B"] < comp["A"] and comp["B"] < comp["D"]


def test_edf_sem_deadline_da_erro():
    with pytest.raises(ValueError):
        run("caso_fcfs_5.json", "EDF")


def test_priority_sem_prioridade_da_erro(tmp_path):
    f = tmp_path / "x.json"
    f.write_text('{"processos":[{"id":"A","chegada":0,"execucao":2}]}')
    cfg = load_input(str(f))
    with pytest.raises(ValueError):
        simulate(cfg.processes, make_algorithm("PRIORITY", 2), 1)


def test_cfs_peso_e_vruntime():
    from algorithms import CFS
    assert CFS.weight(1) == 1.0
    assert CFS.weight(3) == pytest.approx(1.25 ** 2)
    timeline, table, g = run("caso1.json", "CFS")
    # fatias curtas e intercaladas: P1 aparece mais de uma vez separado por outros
    execs = [s.pid for s in timeline if s.kind == "exec"]
    assert len(set(execs[:6])) > 1  # mais de um processo nas primeiras fatias


def test_estouro_de_deadline(tmp_path):
    f = tmp_path / "estouro.json"
    f.write_text('{"quantum":2,"sobrecarga_contexto":1,"processos":['
                 '{"id":"X","chegada":0,"execucao":6,"deadline":4,"prioridade":2},'
                 '{"id":"Y","chegada":1,"execucao":4,"deadline":20,"prioridade":1}]}')
    cfg = load_input(str(f))
    timeline, finished = simulate(cfg.processes, make_algorithm("RR", 2), 1)
    table = {m.pid: m for m in individual_metrics(finished)}
    assert table["X"].deadline_ok is False and table["Y"].deadline_ok is True
    assert global_metrics(list(table.values()), timeline, 1).lost_deadlines == 1


def test_deadline_relativo_vira_absoluto():
    cfg = load_input(str(CASOS / "caso_professor.json"))
    assert [p.new_deadline for p in cfg.processes] == [35, 19, 28, 37]


# ---------- ponta a ponta (CLI, JSON, Gantt, log) ----------

def test_cli_gera_gantt_e_log(tmp_path):
    png, log = tmp_path / "g.png", tmp_path / "l.log"
    rc = main(["--alg", "RR", "--input", str(CASOS / "caso1.json"), "--gantt", str(png), "--log", str(log), "--seed", "42"])
    assert rc == 0 and png.stat().st_size > 1000 and "Algoritmo: RR" in log.read_text(encoding="utf-8")


def test_cli_all_compara_todos(tmp_path, capsys):
    rc = main(["--alg", "ALL", "--input", str(CASOS / "caso_professor.json"), "--gantt", str(tmp_path / "g.png")])
    out = capsys.readouterr().out
    assert rc == 0 and "COMPARAÇÃO" in out and len(list(tmp_path.glob("g_*.png"))) == len(ALGORITHMS)


def test_cli_algoritmo_invalido():
    assert main(["--alg", "XYZ", "--input", str(CASOS / "caso1.json")]) == 1
