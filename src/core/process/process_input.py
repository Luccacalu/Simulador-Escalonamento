from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class ProcessInput:
    """Dado de entrada, imutável. `deadline` é RELATIVO à chegada (o DeadlineReadyProcess
    soma a chegada); o json_reader converte se o JSON trouxer deadline absoluto."""
    id: int | str
    arrival_time: int
    burst_time: int
    deadline: int | None = None
    priority: int | None = None

    def __post_init__(self):
        for name in ('arrival_time', 'burst_time', 'deadline', 'priority'):
            v = getattr(self, name)
            if v is not None and (not isinstance(v, int) or isinstance(v, bool)):
                raise ValueError(f'{name} do processo {self.id} deve ser inteiro')
        if self.burst_time <= 0:
            raise ValueError(f'burst_time do processo {self.id} deve ser > 0')
        if self.deadline is not None and self.deadline <= 0:
            raise ValueError(f'deadline do processo {self.id} deve ser > 0 (relativo à chegada)')
