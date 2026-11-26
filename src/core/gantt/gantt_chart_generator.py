from core.gantt.timestamp import Timestamp
from core.gantt.gantt_chart_data import GanttChartData, Segment
from core.process.process_input import ProcessInput


class GanttChartGenerator:
    def generate(self, timestamps: list[Timestamp], deadlines: dict | None = None,
                 title: str = '', processes: list[ProcessInput] | None = None) -> GanttChartData:
        """`deadlines`: {id: deadline absoluto ou None}, na ordem de chegada (define as linhas)."""
        deadlines = deadlines or {}
        data = GanttChartData(title=title)
        data.rows = [str(k) for k in deadlines]
        data.deadlines = {str(k): v for k, v in deadlines.items() if v is not None}
        process_states = {
            str(p.id): (p.arrival_time, p.burst_time)
            for p in processes or []
        }
        for pid in process_states:
            if pid not in data.rows:
                data.rows.append(pid)
        data.total_time = max((s.t for s in timestamps), default=-1) + 1

        if process_states:
            executed = {pid: 0 for pid in process_states}
            last_by_pid: dict[str, Segment] = {}

            def add_segment(pid: str, t: int, kind: str) -> None:
                last = last_by_pid.get(pid)
                if last and last.kind == kind and last.end == t:
                    last.end += 1
                else:
                    segment = Segment(pid, t, t + 1, kind)
                    data.segments.append(segment)
                    last_by_pid[pid] = segment

            for s in timestamps:
                active: dict[str, str] = {}
                if isinstance(s.pid, tuple):
                    active[str(s.pid[0])] = 'overhead'
                elif s.pid is not None:
                    pid = str(s.pid)
                    deadline = data.deadlines.get(pid)
                    active[pid] = 'late' if deadline is not None and s.t >= deadline else 'exec'

                for pid, (arrival, burst) in process_states.items():
                    if s.t < arrival or executed[pid] >= burst:
                        continue
                    kind = active.get(pid, 'waiting')
                    add_segment(pid, s.t, kind)
                    if kind in ('exec', 'late'):
                        executed[pid] += 1
            return data

        for s in timestamps:
            if s.pid is None:
                continue
            if isinstance(s.pid, tuple):  # sobrecarga: na linha de quem saiu
                pid, kind = str(s.pid[0]), 'overhead'
            else:
                pid = str(s.pid)
                d = data.deadlines.get(pid)
                kind = 'late' if d is not None and s.t >= d else 'exec'
            last = data.segments[-1] if data.segments else None
            if last and last.pid == pid and last.kind == kind and last.end == s.t:
                last.end += 1
            else:
                data.segments.append(Segment(pid, s.t, s.t + 1, kind))
        return data
