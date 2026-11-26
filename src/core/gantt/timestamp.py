from dataclasses import dataclass


@dataclass
class Timestamp:
    """O que a CPU fez em [t, t+1): None = ociosa, id = executando, (de, para) = sobrecarga."""
    t: int
    pid: tuple[int | str, int | str] | int | str | None
