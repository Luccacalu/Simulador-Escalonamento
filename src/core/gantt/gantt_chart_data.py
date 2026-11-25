from dataclasses import dataclass, field


@dataclass
class Segment:
    pid: str       # linha (processo) onde é desenhado
    start: int
    end: int
    kind: str      # exec (verde) | overhead (vermelho) | waiting (amarelo) | late (cinza)


@dataclass
class GanttChartData:
    rows: list[str] = field(default_factory=list)
    segments: list[Segment] = field(default_factory=list)
    deadlines: dict[str, int] = field(default_factory=dict)  # deadline absoluto por processo
    total_time: int = 0
    title: str = ''
