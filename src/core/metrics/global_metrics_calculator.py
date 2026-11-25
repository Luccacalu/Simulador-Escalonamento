from core.metrics.global_metrics import GlobalMetrics
from core.metrics.individual_metrics import IndividualMetrics


class GlobalMetricsCalculator:
    def calculate(self, result_table: list[IndividualMetrics], idle_time: int = 0,
                  total_preemptions: int = 0, overhead_time: int = 0) -> GlobalMetrics:
        n = len(result_table) or 1
        total = max((m.completion_time for m in result_table), default=0)  # fim da simulação
        return GlobalMetrics(
            average_turnaround_time=sum(m.turnaround_time for m in result_table) / n,
            average_waiting_time=sum(m.waiting_time for m in result_table) / n,
            average_response_time=sum(m.response_time for m in result_table) / n,
            lost_deadlines=sum(1 for m in result_table if m.deadline_ok is False),
            throughput=len(result_table) / (total or 1),
            idle_time=idle_time,
            total_preemptions=total_preemptions,
            idle_percent=100 * idle_time / (total or 1),
            overhead_time=overhead_time,
            overhead_percent=100 * overhead_time / (total or 1),
            total_time=total,
        )
