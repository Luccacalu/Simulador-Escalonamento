"""Modelos de dados do simulador: Process (processo) e Slot (1 unidade de tempo na linha do tempo)."""
from dataclasses import dataclass, field


@dataclass
class Process:
    """Um processo. Os campos de entrada vêm do JSON; o resto é preenchido pela simulação.

    deadline é RELATIVO à chegada:
    o instante limite absoluto é `new_deadline = arrival_time + deadline`.
    """
    id: str
    arrival_time: int
    burst_time: int
    deadline: int | None = None
    priority: int | None = None

    # estado da simulação
    remaining_time: int = field(init=False)
    start_time: int | None = field(init=False, default=None)
    completion_time: int | None = field(init=False, default=None)
    vruntime: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        if self.burst_time <= 0:
            raise ValueError(f"{self.id}: burst_time deve ser > 0")
        if self.arrival_time < 0:
            raise ValueError(f"{self.id}: arrival_time deve ser >= 0")
        self.remaining_time = self.burst_time

    @property
    def new_deadline(self) -> int | None:
        """Instante absoluto do deadline (chegada + deadline relativo)."""
        if self.deadline is None:
            return None
        return self.arrival_time + self.deadline

    def clone(self) -> "Process":
        """Cópia limpa (sem estado de simulação) para rodar outro algoritmo."""
        return Process(self.id, self.arrival_time, self.burst_time, self.deadline, self.priority)


@dataclass(frozen=True)
class Slot:
    """O que a CPU fez durante [t, t+1).

    kind: 'exec' (executando pid), 'overhead' (troca de contexto; pid = processo que saiu)
    ou 'idle' (CPU parada esperando chegada; pid = None).
    """
    t: int
    kind: str
    pid: str | None
