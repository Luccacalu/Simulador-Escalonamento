from core.process.process_input import ProcessInput


class ReadyProcess:
    id: int
    arrival_time: int
    burst_time: int
    remaining_time: int
    waiting_time: int = 0
    response_time: int | None = None
    completion_time: int | None = None
    turnaround_time: int | None = None

    def __repr__(self):
        return f"""\nReadyProcess: {{
    id: {self.id},
    arrival_time: {self.arrival_time},
    burst_time: {self.burst_time},
    remaining_time: {self.remaining_time},
    waiting_time: {self.waiting_time},
    response_time: {self.response_time},
    completion_time: {self.completion_time},
    turnaround_time: {self.turnaround_time},
}}\n"""

    def __init__(self, process_input: ProcessInput):
        self.id = process_input.id
        self.arrival_time = process_input.arrival_time
        self.burst_time = process_input.burst_time
        self.remaining_time = process_input.burst_time

    def wait(self):
        self.waiting_time += 1

    def execute(self, instant: int):
        if (self.remaining_time == 0): return

        if (self.response_time is None):
            self.response_time = instant - self.arrival_time

        if (self.remaining_time == 1):
            self.completion_time = instant + 1
            self.turnaround_time = self.completion_time - self.arrival_time

        self.remaining_time -= 1
