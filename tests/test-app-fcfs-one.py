import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from dataclasses import dataclass

from core.process.process_input import ProcessInput
from core.process.process_input_list import ProcessInputList
from core.process.ready_process import ReadyProcess
from core.engine.algorithms.fcfs import FCFS
from app import app

from metrics import Metrics, check_metrics

# As entradas
p_list = ProcessInputList([
    ProcessInput(id=1, arrival_time=0, burst_time=10, priority=3),
    ProcessInput(id=2, arrival_time=1, burst_time=6, priority=5),
    ProcessInput(id=3, arrival_time=2, burst_time=2, priority=2),
    ProcessInput(id=4, arrival_time=3, burst_time=4, priority=1),
    ProcessInput(id=5, arrival_time=4, burst_time=8, priority=4),
])

# saída esperada
metrics_list = [
    Metrics(id=1, arrival_time=0, burst_time=10, remaining_time=0, waiting_time=0, response_time=0, completion_time=10, turnaround_time=10),
    Metrics(id=2, arrival_time=1, burst_time=6, remaining_time=0, waiting_time=9, response_time=9, completion_time=16, turnaround_time=15),
    Metrics(id=3, arrival_time=2, burst_time=2, remaining_time=0, waiting_time=14, response_time=14, completion_time=18, turnaround_time=16),
    Metrics(id=4, arrival_time=3, burst_time=4, remaining_time=0, waiting_time=15, response_time=15, completion_time=22, turnaround_time=19),
    Metrics(id=5, arrival_time=4, burst_time=8, remaining_time=0, waiting_time=18, response_time=18, completion_time=30, turnaround_time=26),
]

def check_result(ready_queue: list[ReadyProcess], metrics_list: list[Metrics]):
    assert len(ready_queue) == 5, 'ready_queue should have 5 process'
    print('ready_queue has 5 process, OK')

    for i in range(len(metrics_list)):
        assert check_metrics(ready_queue[i], metrics_list[i]) == True, f'{ready_queue[i]} != {metrics_list[i]}'
        print(f'expected metrics for process {ready_queue[i].id}, OK')

# algoritmo de escalonamento
fcfs = FCFS()

# execução
ready_queue = app(p_list, fcfs)

# verificação
check_result(ready_queue, metrics_list)
