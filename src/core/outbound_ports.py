from typing import Protocol

from core.gantt.gantt_chart_data import GanttChartData
from core.gantt.timestamp import Timestamp
from core.inbound_ports import SimulationConfig
from core.process.process_input_list import ProcessInputList


class InputReader(Protocol):
    def read(self, path: str) -> tuple[SimulationConfig, ProcessInputList]: ...


class LogWriter(Protocol):
    def write(self, path: str, timestamps: list[Timestamp], extra: str = '') -> None: ...


class ImageGenerator(Protocol):
    def save(self, data: GanttChartData, path: str) -> None: ...
