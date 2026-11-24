# importar as classes e construir a aplicação aqui
from dataclasses import dataclass

from core.process.process_input import ProcessInput
from core.process.process_input_list import ProcessInputList
from core.process.ready_process import ReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm

# Esse é um esboço de como dividir as responsabilidades entre os objetos que fazem parte do núcleo da aplicação

# As entradas
p_list = ProcessInputList([
    ProcessInput(id=1, arrival_time=0, burst_time=10, priority=3),
    ProcessInput(id=2, arrival_time=1, burst_time=6, priority=5),
    ProcessInput(id=3, arrival_time=2, burst_time=2, priority=2),
    ProcessInput(id=4, arrival_time=3, burst_time=4, priority=1),
    ProcessInput(id=5, arrival_time=4, burst_time=8, priority=4),
])

def execute_round(ready_queue: list[ReadyProcess], next: ReadyProcess, time: int):
    next.execute(time)
    for rp in ready_queue:
        if (rp == next): continue
        if (rp.completion_time is not None): continue
        if (time < rp.arrival_time): continue
        rp.wait()

def app(p_list: ProcessInputList, alg: SchedulingAlgorithm) -> list[ReadyProcess]:
    # Engine.run(...)
    time = 0
    quantum = 0

    # onde entra o logger?
    # o scheduling algorithm decide o quantum e o proximo a ser executado
    # FCFS
    ready_queue = [ReadyProcess(p) for p in p_list.get_arrived(time)]

    # O SchedulingAlgorithm vai retornar quem é o next a ser Executado pelo ProcessExecutor
    # a engine é dona da ready_queue
    # o fcfs --|> SchedulingAlgorithm é dono da estrutura que organiza e calcula qual é o próximo processo e o quantum que ele deve receber
    # engine.run(...)
    #
    next = None

    # roda tudo
    for rp in ready_queue:
        next, quantum = alg.next(next, ready_queue) # obtem o proximo a ser executado e o quantum do SchedulingAlgorithm
        for _ in range(quantum):
            # process_executor.execute(...)
            execute_round(ready_queue, next, time) # executa o processo da vez por uma unidade de tempo

            # engine.update()
            time += 1 # acumula essa unidade de tempo
            ready_queue.extend([ReadyProcess(p) for p in p_list.get_arrived(time)]) # busca mais processos dentro da lista

    return ready_queue
