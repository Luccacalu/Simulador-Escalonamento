from pathlib import Path

import pytest

from app import ALL_ALGORITHMS, Simulator, app
from core.engine.algorithms.fcfs import FCFS
from core.process.process_input import ProcessInput
from core.process.process_input_list import ProcessInputList
from external.json_reader import JsonReader

CASOS = Path(__file__).resolve().parents[1] / 'casos'


def run(alg, caso):
    config, procs = JsonReader().read(str(CASOS / caso))
    return Simulator().run(alg, config, procs)


def avg_turnaround(r):
    return r.metrics.average_turnaround_time


# --- (A,B,C,D chegam em 0,4,8,12; exec 8,4,2,7; q=2; sobrecarga=1)
def test_professor_fifo():
    r = run('FCFS', 'caso_professor.json')
    assert [m.turnaround_time for m in r.table] == [8, 8, 6, 9]
    assert avg_turnaround(r) == 7.75


def test_professor_sjf():
    r = run('SJF', 'caso_professor.json')
    assert [m.turnaround_time for m in r.table] == [8, 10, 2, 9]
    assert avg_turnaround(r) == 7.25


def test_professor_rr():
    r = run('RR', 'caso_professor.json')
    assert [m.turnaround_time for m in r.table] == [21, 12, 6, 16]
    assert avg_turnaround(r) == 13.75


def test_gantt_marca_espera_de_processos_prontos():
    r = run('RR', 'caso_professor.json')

    def kind_at(pid, t):
        return next((s.kind for s in r.gantt.segments
                     if s.pid == pid and s.start <= t < s.end), None)

    assert kind_at('B', 3) is None
    assert kind_at('B', 4) == 'waiting'
    assert kind_at('B', 5) == 'waiting'
    assert kind_at('B', 6) == 'exec'
    assert kind_at('A', 2) == 'overhead'
    assert kind_at('A', 6) == 'waiting'
    assert kind_at('C', 11) == 'waiting'
    assert kind_at('B', 16) is None


def test_professor_edf_todos_cumprem():
    r = run('EDF', 'caso_professor.json')
    assert [m.turnaround_time for m in r.table] == [18, 7, 5, 16]
    assert avg_turnaround(r) == 11.5
    assert r.metrics.lost_deadlines == 0


# --- FCFS com 5 processos, sem sobrecarga
def test_fcfs_cinco_processos():
    procs = ProcessInputList([
        ProcessInput(id=1, arrival_time=0, burst_time=10, priority=3),
        ProcessInput(id=2, arrival_time=1, burst_time=6, priority=5),
        ProcessInput(id=3, arrival_time=2, burst_time=2, priority=2),
        ProcessInput(id=4, arrival_time=3, burst_time=4, priority=1),
        ProcessInput(id=5, arrival_time=4, burst_time=8, priority=4),
    ])
    config, _ = JsonReader().read(str(CASOS / 'caso1.json'))
    r = Simulator().run('FCFS', config, procs)
    assert [m.waiting_time for m in r.table] == [0, 9, 14, 15, 18]
    assert [m.response_time for m in r.table] == [0, 9, 14, 15, 18]
    assert [m.completion_time for m in r.table] == [10, 16, 18, 22, 30]


# --- propriedades gerais, para todos os algoritmos e casos
@pytest.mark.parametrize('alg', ALL_ALGORITHMS)
@pytest.mark.parametrize('caso', ['caso1.json', 'caso_ocioso.json', 'caso_professor.json'])
def test_invariantes(alg, caso):
    r = run(alg, caso)
    n = len(r.table)
    assert n >= 3
    for m in r.table:
        assert m.turnaround_time == m.completion_time - m.arrival_time
        assert m.waiting_time == m.turnaround_time - m.burst_time >= 0
        assert m.start_time >= m.arrival_time
    # cada processo executa exatamente seu burst
    for m in r.table:
        executed = sum(1 for s in r.timestamps if s.pid == m.pid)
        assert executed == m.burst_time
    # a CPU nunca faz duas coisas ao mesmo tempo, e o tempo é contínuo
    assert [s.t for s in r.timestamps] == list(range(r.metrics.total_time))
    exec_t = sum(m.burst_time for m in r.table)
    assert exec_t + r.metrics.idle_time + r.metrics.overhead_time == r.metrics.total_time


def test_cpu_ociosa():
    r = run('FCFS', 'caso_ocioso.json')
    assert r.metrics.idle_time == (10 - 3) + (25 - 16)  # P1 acaba em 3; P3 acaba em 16
    assert any(s.pid is None for s in r.timestamps)


def test_caso_base_preemptivo_tem_sobrecarga():
    r = run('RR', 'caso1.json')
    assert r.metrics.overhead_time == r.metrics.total_preemptions  # sobrecarga = 1
    assert r.metrics.total_preemptions > 0


def test_cfs_alterna_justo():
    r = run('CFS', 'caso1.json')
    seq = [s.pid for s in r.timestamps if isinstance(s.pid, str)]
    assert len({*seq}) == 3 and seq != sorted(seq)  # intercala execuções curtas


def test_edf_exige_deadline():
    procs = ProcessInputList([ProcessInput(id='X', arrival_time=0, burst_time=2)])
    config, _ = JsonReader().read(str(CASOS / 'caso1.json'))
    with pytest.raises(Exception):
        Simulator().run('EDF', config, procs)


def test_app_devolve_ready_queue():
    p = ProcessInputList([ProcessInput(id=1, arrival_time=0, burst_time=3),
                            ProcessInput(id=2, arrival_time=1, burst_time=2)])
    rq = app(p, FCFS())
    assert [(r.id, r.waiting_time, r.completion_time) for r in rq] == [(1, 0, 3), (2, 2, 5)]


def test_deadline_absoluto_do_json():
    r = run('EDF', 'caso1.json')
    assert [m.deadline for m in r.table] == [8, 12, 20]  # absolutos, como no enunciado
