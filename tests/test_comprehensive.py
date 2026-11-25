import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from app import ALL_ALGORITHMS, Simulator
from core.process.process_input import ProcessInput
from core.process.process_input_list import ProcessInputList
from external.json_reader import JsonReader


CASOS = ROOT / 'casos'
ALGORITHMS = ['FCFS', 'FIFO', 'SJF', 'RR', 'PRIORITY', 'EDF', 'CFS', 'AUTORAL']


def read_case(name):
    return JsonReader().read(str(CASOS / name))


def run(algorithm, name='caso1.json', quantum=None, overhead=None):
    config, processes = read_case(name)
    if quantum is not None:
        config.quantum = quantum
    if overhead is not None:
        config.overhead = overhead
    return Simulator().run(algorithm, config, processes)


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('quantum', [1, 2, 5])
@pytest.mark.parametrize('overhead', [0, 1, 3])
def test_all_algorithm_parameter_combinations(algorithm, quantum, overhead):
    if algorithm == 'EDF':
        name = 'caso_professor.json'
    else:
        name = 'caso1.json'
    result = run(algorithm, name, quantum=quantum, overhead=overhead)

    assert result.table
    assert result.metrics.total_time >= max(m.completion_time for m in result.table)
    assert result.metrics.idle_percent >= 0
    assert result.metrics.overhead_percent >= 0
    assert result.metrics.throughput > 0

    for metric in result.table:
        assert metric.turnaround_time == metric.completion_time - metric.arrival_time
        assert metric.waiting_time == metric.turnaround_time - metric.burst_time
        assert metric.waiting_time >= 0
        assert metric.response_time >= 0


@pytest.mark.parametrize('algorithm', ALL_ALGORITHMS)
@pytest.mark.parametrize('case', ['caso1.json', 'caso_ocioso.json', 'caso_professor.json'])
@pytest.mark.parametrize('overhead', [0, 1, 4])
def test_property_invariants_all_algorithms_and_cases(algorithm, case, overhead):
    if algorithm == 'EDF' and case == 'caso1.json':
        result = run(algorithm, case, quantum=2, overhead=overhead)
    else:
        result = run(algorithm, case, quantum=2, overhead=overhead)

    timestamps = result.timestamps
    table = result.table
    assert [stamp.t for stamp in timestamps] == list(range(result.metrics.total_time))
    assert sum(m.burst_time for m in table) + result.metrics.idle_time + result.metrics.overhead_time == result.metrics.total_time

    for metric in table:
        executed = sum(
            1 for stamp in timestamps
            if stamp.pid == metric.pid
            or (isinstance(stamp.pid, tuple) and stamp.pid[0] == metric.pid)
        )
        if result.metrics.overhead_time:
            assert executed >= metric.burst_time
        else:
            assert executed == metric.burst_time
        assert metric.start_time >= metric.arrival_time
        assert metric.completion_time >= metric.start_time


@pytest.mark.parametrize('seed', [None, 0, 1, 42, 99999])
def test_seed_values_do_not_break_deterministic_execution(seed):
    config, processes = read_case('caso1.json')
    config.seed = seed
    first = Simulator().run('CFS', config, processes)

    config, processes = read_case('caso1.json')
    config.seed = seed
    second = Simulator().run('CFS', config, processes)

    assert [(m.pid, m.completion_time) for m in first.table] == [
        (m.pid, m.completion_time) for m in second.table
    ]


@pytest.mark.parametrize('arrival, burst, deadline', [
    (0, 1, 0),
    (0, 1, None),
    (5, 3, 20),
    (100, 1, 100),
])
def test_process_boundary_values(arrival, burst, deadline):
    process = ProcessInput(id='X', arrival_time=arrival, burst_time=burst, deadline=deadline)
    processes = ProcessInputList([process])
    config, _ = read_case('caso1.json')
    result = Simulator().run('FCFS', config, processes)
    assert result.table[0].arrival_time == arrival
    assert result.table[0].burst_time == burst
    assert result.table[0].completion_time >= arrival + burst


@pytest.mark.parametrize('kwargs, message', [
    ({'id': 'X', 'arrival_time': -1, 'burst_time': 1}, 'arrival_time'),
    ({'id': 'X', 'arrival_time': 0, 'burst_time': 0}, 'burst_time'),
    ({'id': 'X', 'arrival_time': 0, 'burst_time': -1}, 'burst_time'),
    ({'id': 'X', 'arrival_time': True, 'burst_time': 1}, 'arrival_time'),
    ({'id': 'X', 'arrival_time': 0, 'burst_time': True}, 'burst_time'),
    ({'id': 'X', 'arrival_time': 0, 'burst_time': 1, 'deadline': True}, 'deadline'),
])
def test_invalid_process_values_are_rejected(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ProcessInput(**kwargs)


def test_duplicate_process_ids_are_rejected():
    with pytest.raises(ValueError, match='únicos'):
        ProcessInputList([
            ProcessInput(id='A', arrival_time=0, burst_time=1),
            ProcessInput(id='A', arrival_time=1, burst_time=1),
        ])


@pytest.mark.parametrize('algorithm', ['EDF', 'PRIORITY'])
def test_algorithms_requiring_process_attributes_reject_missing_data(algorithm):
    config, _ = read_case('caso1.json')
    process = ProcessInput(id='A', arrival_time=0, burst_time=1)
    with pytest.raises(Exception):
        Simulator().run(algorithm, config, ProcessInputList([process]))


def test_unknown_algorithm_is_rejected():
    config, processes = read_case('caso1.json')
    with pytest.raises(ValueError, match='Algoritmo desconhecido'):
        Simulator().run('LIFO', config, processes)


@pytest.mark.parametrize('algorithm', ['RR', 'PRIORITY', 'EDF', 'CFS', 'AUTORAL'])
def test_preemptive_algorithms_reject_zero_quantum(algorithm):
    config, processes = read_case('caso_professor.json')
    config.quantum = 0
    with pytest.raises(ValueError, match='exige quantum > 0'):
        Simulator().run(algorithm, config, processes)


def test_relative_and_absolute_deadlines(tmp_path):
    absolute = tmp_path / 'absolute.json'
    absolute.write_text(json.dumps({
        'deadline_relativo': False,
        'quantum': 2,
        'sobrecarga_contexto': 1,
        'processos': [
            {'id': 'A', 'chegada': 5, 'execucao': 2, 'deadline': 10},
        ],
    }), encoding='utf-8')
    result = Simulator().run('EDF', *JsonReader().read(str(absolute)))
    assert result.table[0].deadline == 10
    assert result.table[0].completion_time == 7
    assert result.table[0].deadline_ok is True

    relative = tmp_path / 'relative.json'
    relative.write_text(json.dumps({
        'deadline_relativo': True,
        'quantum': 2,
        'sobrecarga_contexto': 1,
        'processos': [
            {'id': 'A', 'chegada': 5, 'execucao': 2, 'deadline': 10},
        ],
    }), encoding='utf-8')
    result = Simulator().run('EDF', *JsonReader().read(str(relative)))
    assert result.table[0].deadline == 15
    assert result.table[0].completion_time == 7
    assert result.table[0].deadline_ok is True


@pytest.mark.parametrize('root', [
    [],
    {'processos': None},
    {'processos': {}},
    {'processos': [None]},
    {'processos': [{'id': 'A', 'chegada': 0}]},
])
def test_invalid_json_shapes_are_rejected(tmp_path, root):
    path = tmp_path / 'invalid.json'
    path.write_text(json.dumps(root), encoding='utf-8')
    with pytest.raises((ValueError, TypeError)):
        JsonReader().read(str(path))


@pytest.mark.parametrize('field,value,message', [
    ('quantum', 0, 'quantum'),
    ('quantum', '2', 'quantum'),
    ('sobrecarga_contexto', -1, 'sobrecarga_contexto'),
    ('sobrecarga_contexto', '1', 'sobrecarga_contexto'),
    ('seed', '42', 'seed'),
])
def test_invalid_json_configuration_is_rejected(tmp_path, field, value, message):
    path = tmp_path / 'invalid_config.json'
    path.write_text(json.dumps({
        field: value,
        'processos': [{'id': 'A', 'chegada': 0, 'execucao': 1}],
    }), encoding='utf-8')
    with pytest.raises(ValueError, match=message):
        JsonReader().read(str(path))


def test_gantt_and_log_are_created_for_every_algorithm(tmp_path):
    gantt = tmp_path / 'reports' / 'case.png'
    log = tmp_path / 'reports' / 'case.log'
    command = [
        sys.executable, str(ROOT / 'main.py'),
        '--alg', 'ALL',
        '--input', str(CASOS / 'caso1.json'),
        '--gantt', str(gantt),
        '--log', str(log),
        '--seed', '42',
        '--quantum', '2',
        '--overhead', '1',
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    assert '=== COMPARAÇÃO ===' in completed.stdout

    for algorithm in ALL_ALGORITHMS:
        assert gantt.with_name(f'case_{algorithm}.png').is_file()
        assert log.with_name(f'case_{algorithm}.log').is_file()


@pytest.mark.parametrize('algorithm', ALGORITHMS)
def test_cli_single_algorithm_execution(algorithm):
    completed = subprocess.run(
        [sys.executable, str(ROOT / 'main.py'), '--alg', algorithm,
         '--input', str(CASOS / 'caso_professor.json')],
        cwd=ROOT, text=True, capture_output=True,
    )
    if algorithm == 'EDF':
        assert completed.returncode == 0
    else:
        assert completed.returncode == 0
    expected_name = algorithm
    assert f'=== {expected_name} ===' in completed.stdout


@pytest.mark.parametrize('arguments, expected', [
    (['--alg', 'NOPE', '--input', 'casos/caso1.json'], 'Algoritmo desconhecido'),
    (['--alg', 'RR', '--input', 'casos/caso1.json', '--quantum', '0'], 'quantum deve ser > 0'),
    (['--alg', 'FCFS', '--input', 'casos/caso1.json', '--overhead', '-1'], 'sobrecarga_contexto deve ser >= 0'),
])
def test_cli_rejects_invalid_arguments(arguments, expected):
    completed = subprocess.run(
        [sys.executable, str(ROOT / 'main.py'), *arguments],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert completed.returncode != 0
    assert expected in completed.stderr


def test_cli_help_lists_every_option():
    completed = subprocess.run(
        [sys.executable, str(ROOT / 'main.py'), '--help'],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert completed.returncode == 0
    for option in ['--alg', '--input', '--gantt', '--log', '--seed',
                   '--quantum', '--overhead', '--delay']:
        assert option in completed.stdout


@pytest.mark.parametrize('algorithm', ['FCFS', 'SJF', 'RR', 'PRIORITY', 'EDF', 'CFS', 'AUTORAL'])
def test_delay_mode_preserves_final_report(algorithm):
    completed = subprocess.run(
        [sys.executable, str(ROOT / 'main.py'),
         '--alg', algorithm,
         '--input', str(CASOS / 'caso_professor.json'),
         '--delay', '1',
         '--quantum', '2',
         '--overhead', '1'],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert completed.returncode == 0
    assert 'CPU ociosa' in completed.stdout or 'CPU com Processo' in completed.stdout
    assert 'Turnaround médio' in completed.stdout


def test_randomized_property_suite():
    rng = random.Random(20261124)
    for _ in range(25):
        count = rng.randint(1, 8)
        processes = []
        for i in range(count):
            processes.append(ProcessInput(
                id=f'P{i}',
                arrival_time=rng.randint(0, 15),
                burst_time=rng.randint(1, 10),
                deadline=rng.randint(1, 40),
                priority=rng.randint(1, 5),
            ))
        process_list = ProcessInputList(processes)
        quantum = rng.randint(1, 5)
        overhead = rng.randint(0, 4)

        for algorithm in ['FCFS', 'SJF', 'RR', 'PRIORITY', 'EDF', 'CFS', 'AUTORAL']:
            config = type('Config', (), {
                'quantum': quantum,
                'overhead': overhead,
                'seed': 42,
            })()
            result = Simulator().run(algorithm, config, ProcessInputList(processes))

            assert [stamp.t for stamp in result.timestamps] == list(range(result.metrics.total_time))
            assert sum(m.burst_time for m in result.table) + result.metrics.idle_time + result.metrics.overhead_time == result.metrics.total_time
            for metric in result.table:
                assert metric.turnaround_time == metric.completion_time - metric.arrival_time
                assert metric.waiting_time == metric.turnaround_time - metric.burst_time
