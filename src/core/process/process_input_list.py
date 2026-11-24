from core.process.process_input import ProcessInput


class ProcessInputList:
    _list: list[ProcessInput]

    def __init__(self, processInputs: list[ProcessInput]) -> None:
        self._list = processInputs


    def get_arrived(self, time: int) -> list[ProcessInput]:
        arrived, not_arrived = [], []
        for p in self._list:
            (arrived if time >= p.arrival_time else not_arrived).append(p)


        self._list = not_arrived
        return arrived
