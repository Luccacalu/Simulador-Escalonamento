from timestamp import Timestamp


class ExecutionLogger:
    timestamps: list[Timestamp]

    def set_timestamp(self, time: int, pid: tuple[int, int] | int | None):
        pass

    def get_timestamps(self) -> list[Timestamp]:
        return self.timestamps
