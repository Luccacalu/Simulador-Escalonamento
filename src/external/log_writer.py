import os

from core.gantt.timestamp import Timestamp


def format_stamp(s: Timestamp) -> str:
    if s.pid is None:
        return f'Tempo {s.t}: CPU ociosa'
    if isinstance(s.pid, tuple):
        return f'Tempo {s.t}: CPU com Processo {s.pid}  (sobrecarga de contexto)'
    return f'Tempo {s.t}: CPU com Processo {s.pid}'


class LogWriter:
    def write(self, path: str, timestamps: list[Timestamp], extra: str = '') -> None:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(format_stamp(s) for s in timestamps) + '\n')
            if extra:
                f.write('\n' + extra + '\n')
