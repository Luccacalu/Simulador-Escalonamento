from scheduling_algorithm import SchedulingAlgorithm
from process_executor import ProcessExecutor
from core.process.process_input_list import ProcessInputList
from core.metrics.individual_metrics import IndividualMetrics
from core.gantt.execution_logger import ExecutionLogger


class Engine:
    current_time: int
    alg: SchedulingAlgorithm
    input_process_list: ProcessInputList
    executor: ProcessExecutor

    def run(self, logger: ExecutionLogger | None) -> list[IndividualMetrics]:
        return []
