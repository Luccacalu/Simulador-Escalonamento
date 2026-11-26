from core.process.process_input import ProcessInput


class ProcessInputList:
    _list: list[ProcessInput]

    def __init__(self, processInputs: list[ProcessInput]) -> None:
        ids = [p.id for p in processInputs]
        if len(ids) != len(set(ids)):
            raise ValueError('ids de processos devem ser únicos')
        self._list = sorted(processInputs, key=lambda p: p.arrival_time)  # estável


    def get_arrived(self, time: int) -> list[ProcessInput]:
        arrived, not_arrived = [], []
        for p in self._list:
            (arrived if time >= p.arrival_time else not_arrived).append(p)


        self._list = not_arrived
        return arrived

    def next_arrival(self) -> int | None:
        return self._list[0].arrival_time if self._list else None

    def empty(self) -> bool:
        return not self._list
