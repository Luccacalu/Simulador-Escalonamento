from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class ProcessExecutor:
    on_cpu: None | ReadyProcess | tuple[ReadyProcess, ReadyProcess]
    ready_queue: list[ReadyProcess]

    def enqueue(self, process_input_list: list[ProcessInput]):
        for p in process_input_list:
            self.ready_queue.append(ReadyProcess(p))

    def execute(self, pid: int, time: int, quantum: int):
        for rp in self.ready_queue:
            if (rp.id == pid):
                self.on_cpu = rp
                rp.execute(time)
            else:
                rp.wait()

    def preempt_execute(self, pid: int, time: int, quantum):
        pass

    def get_state(self) -> list[ReadyProcess]:
        return self.ready_queue.copy()
