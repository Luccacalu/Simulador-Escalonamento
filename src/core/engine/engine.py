from core.engine.scheduling_algorithm import SchedulingAlgorithm
from core.engine.process_executor import ProcessExecutor
from core.process.process_input_list import ProcessInputList
from core.metrics.individual_metrics import IndividualMetrics
from core.gantt.execution_logger import ExecutionLogger


class Engine:
    """Simulador de eventos discretos (CPU single-core, passo de 1 u.t.).

    Convenções:
      * a sobrecarga é cobrada ao fim de toda fatia em que o processo NÃO termina
        (mesmo que ele continue); ao terminar, o próximo começa sem sobrecarga;
      * o escalonador só decide nas fronteiras de fatia;
      * chegadas são admitidas a cada u.t. (inclusive durante a sobrecarga e a ociosidade).
    """
    current_time: int
    alg: SchedulingAlgorithm
    input_process_list: ProcessInputList
    executor: ProcessExecutor

    def __init__(self, alg: SchedulingAlgorithm, input_process_list: ProcessInputList,
                 executor: ProcessExecutor | None = None):
        self.current_time = 0
        self.alg = alg
        self.input_process_list = input_process_list
        self.executor = executor or ProcessExecutor(alg.ready_class)
        self.idle_time = 0
        self.overhead_time = 0
        self.preemptions = 0

    def _admit(self):
        self.executor.enqueue(self.input_process_list.get_arrived(self.current_time))

    def run(self, logger: ExecutionLogger | None = None) -> list[IndividualMetrics]:
        logger = logger or ExecutionLogger()
        ex, inputs = self.executor, self.input_process_list
        overhead = self.alg.overload or 0
        on_cpu = None
        overhead_ticks: list[int] = []  # instantes de sobrecarga ainda sem o "para quem"

        self._admit()
        while True:
            if not self.alg.pending(ex.ready_queue):
                if inputs.empty():
                    break
                logger.set_timestamp(self.current_time, None)  # CPU ociosa até a próxima chegada
                self.current_time += 1
                self.idle_time += 1
                self._admit()
                continue

            p, quantum = self.alg.next(on_cpu, ex.get_state())
            for t in overhead_ticks:
                logger.set_timestamp(t, (on_cpu.id, p.id))
            overhead_ticks = []

            for _ in range(quantum):
                logger.set_timestamp(self.current_time, p.id)
                ex.execute(p.id, self.current_time, quantum)
                self.current_time += 1
                self._admit()
            on_cpu = p

            if p.completion_time is None:  # fatia acabou, processo não: troca de contexto
                self.preemptions += 1
                for _ in range(overhead):
                    overhead_ticks.append(self.current_time)
                    ex.preempt_execute(p.id, self.current_time, quantum)
                    self.current_time += 1
                    self.overhead_time += 1
                    self._admit()

        return [IndividualMetrics(rp) for rp in ex.ready_queue]
