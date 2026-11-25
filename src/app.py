# importar as classes e construir a aplicação aqui
from core.process.process_input_list import ProcessInputList
from core.process.ready_process import ReadyProcess
from core.engine.scheduling_algorithm import SchedulingAlgorithm
from core.engine.engine import Engine
from core.engine.algorithms.fcfs import FCFS
from core.engine.algorithms.sjf import SJF
from core.engine.algorithms.rr import RoundRobin
from core.engine.algorithms.priority import Priority
from core.engine.algorithms.edf import EDF
from core.engine.algorithms.cfs import CFS
from core.engine.algorithms.autoral import Autoral
from core.gantt.execution_logger import ExecutionLogger
from core.gantt.gantt_chart_generator import GanttChartGenerator
from core.inbound_ports import SimulationConfig, SimulationResult
from core.metrics.global_metrics_calculator import GlobalMetricsCalculator

ALGORITHMS = {
    'FCFS': FCFS, 'FIFO': FCFS, 'SJF': SJF, 'RR': RoundRobin,
    'PRIORITY': Priority, 'EDF': EDF, 'CFS': CFS, 'AUTORAL': Autoral,
}
ALL_ALGORITHMS = ['FCFS', 'SJF', 'RR', 'PRIORITY', 'EDF', 'CFS', 'AUTORAL']


def app(p_list: ProcessInputList, alg: SchedulingAlgorithm) -> list[ReadyProcess]:
    """Roda a simulação e devolve a ready_queue com todos os processos já concluídos."""
    engine = Engine(alg, p_list)
    engine.run()
    return engine.executor.ready_queue


class Simulator:
    """Implementa a porta de entrada (SimulationUseCase)."""

    def run(self, algorithm: str, config: SimulationConfig,
            processes: ProcessInputList) -> SimulationResult:
        name = algorithm.upper()
        if name not in ALGORITHMS:
            raise ValueError(f'Algoritmo desconhecido: {algorithm}. Use: {", ".join(ALGORITHMS)} ou ALL')
        alg = ALGORITHMS[name](quantum=config.quantum, overload=config.overhead, seed=config.seed)

        process_inputs = processes._list.copy()
        deadlines = {p.id: (None if p.deadline is None else p.deadline + p.arrival_time)
                     for p in process_inputs}  # ordem de chegada
        engine = Engine(alg, processes)
        logger = ExecutionLogger()
        table = engine.run(logger)

        metrics = GlobalMetricsCalculator().calculate(
            table, idle_time=engine.idle_time, total_preemptions=engine.preemptions,
            overhead_time=engine.overhead_time)
        gantt = GanttChartGenerator().generate(
            logger.get_timestamps(), deadlines, title=name, processes=process_inputs)
        return SimulationResult(name, table, metrics, logger.get_timestamps(), gantt)
