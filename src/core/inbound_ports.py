from dataclasses import dataclass
from typing import Protocol

from core.gantt.gantt_chart_data import GanttChartData
from core.gantt.timestamp import Timestamp
from core.metrics.global_metrics import GlobalMetrics
from core.metrics.individual_metrics import IndividualMetrics
from core.process.process_input_list import ProcessInputList


@dataclass
class SimulationConfig:
    quantum: int | None = 2
    overhead: int = 1            # sobrecarga_contexto
    seed: int | None = None
    disk_cost: int = 0           # custo_disco (bônus de memória virtual: não usado)


@dataclass
class SimulationResult:
    algorithm: str
    table: list[IndividualMetrics]
    metrics: GlobalMetrics
    timestamps: list[Timestamp]
    gantt: GanttChartData


class SimulationUseCase(Protocol):
    """Porta de entrada: o que o mundo externo (CLI) pede ao domínio."""

    def run(self, algorithm: str, config: SimulationConfig,
            processes: ProcessInputList) -> SimulationResult: ...
