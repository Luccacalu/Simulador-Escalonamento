from core.gantt.timestamp import Timestamp


class ExecutionLogger:
    timestamps: list[Timestamp]

    def __init__(self) -> None:
        self.timestamps = []

    def set_timestamp(self, time: int, pid: tuple[int | str, int | str] | int | str | None):
        self.timestamps.append(Timestamp(time, pid))

    def get_timestamps(self) -> list[Timestamp]:
        return self.timestamps
