from core.process.process_input import ProcessInput
from core.process.ready_process import ReadyProcess


class ProcessExecutor:
    on_cpu: None | ReadyProcess | tuple[ReadyProcess, ReadyProcess]
    ready_queue: list[ReadyProcess]  # todos os que já chegaram (os concluídos permanecem, em ordem de chegada)

    def __init__(self, ready_class: type[ReadyProcess] = ReadyProcess):
        self.ready_class = ready_class
        self.on_cpu = None
        self.ready_queue = []

    def enqueue(self, process_input_list: list[ProcessInput]):
        for p in process_input_list:
            self.ready_queue.append(self.ready_class(p))

    def execute(self, pid: int | str, time: int, quantum: int | None = None):
        """1 u.t. de execução de `pid`; os demais não concluídos esperam."""
        for rp in self.ready_queue:
            if (rp.id == pid):
                self.on_cpu = rp
                rp.execute(time)
            elif (rp.completion_time is None):
                rp.wait()

    def preempt_execute(self, pid: int | str, time: int, quantum: int | None = None):
        """1 u.t. de sobrecarga de troca de contexto: CPU ociosa, todos os não concluídos esperam.
        `on_cpu` continua sendo o processo preemptado `pid` (o algoritmo o reinsere na fila)."""
        for rp in self.ready_queue:
            if (rp.completion_time is None):
                rp.wait()

    def get_state(self) -> list[ReadyProcess]:
        return self.ready_queue.copy()
