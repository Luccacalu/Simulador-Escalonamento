from dataclasses import dataclass


@dataclass(kw_only=True)
class ProcessInput:
    id: int
    arrival_time: int
    burst_time: int
    deadline: int | None = None
    priority: int | None = None

# p = ProcessInput(id='j', arrival_time=2, burst_time=3) da erro na IDE, mas roda
# p = ProcessInput(id=1, arrival_time=2, burst_time=3)
# p = ProcessInput(id=1, arrival_time=2, burst_time=3, deadline=10)
# p = ProcessInput(id=1, arrival_time=2, burst_time=3, deadline=10, priority=2)
# print(p)
