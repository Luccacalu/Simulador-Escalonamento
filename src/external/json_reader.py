import json

from core.inbound_ports import SimulationConfig
from core.process.process_input import ProcessInput
from core.process.process_input_list import ProcessInputList


class JsonReader:
    """Lê o JSON do enunciado. O deadline do JSON é ABSOLUTO (enunciado); internamente o
    ProcessInput guarda deadline relativo à chegada, então convertemos aqui. Com
    `"deadline_relativo": true` o valor já é relativo"""

    def read(self, path: str) -> tuple[SimulationConfig, ProcessInputList]:
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise ValueError('o conteúdo raiz do JSON deve ser um objeto')
        if 'processos' not in raw or not isinstance(raw['processos'], list):
            raise ValueError('o JSON deve conter "processos" como uma lista')
        config = SimulationConfig(
            quantum=raw.get('quantum', 2),
            overhead=raw.get('sobrecarga_contexto', 0),
            seed=raw.get('seed'),
            disk_cost=raw.get('custo_disco', 0),
        )
        if config.quantum is not None and (not isinstance(config.quantum, int)
                                           or isinstance(config.quantum, bool)):
            raise ValueError('quantum deve ser inteiro')
        if config.quantum is not None and config.quantum <= 0:
            raise ValueError('quantum deve ser > 0')
        if not isinstance(config.overhead, int) or isinstance(config.overhead, bool):
            raise ValueError('sobrecarga_contexto deve ser inteiro')
        if config.overhead < 0:
            raise ValueError('sobrecarga_contexto deve ser >= 0')
        if config.seed is not None and (not isinstance(config.seed, int)
                                        or isinstance(config.seed, bool)):
            raise ValueError('seed deve ser inteiro')
        relative = raw.get('deadline_relativo', False)
        processes = []
        for r in raw['processos']:
            if not isinstance(r, dict):
                raise ValueError('cada elemento de "processos" deve ser um objeto')
            if 'id' not in r or 'chegada' not in r or 'execucao' not in r:
                raise ValueError('cada processo deve conter id, chegada e execucao')
            dl = r.get('deadline')
            if dl is not None and not relative:
                dl -= r['chegada']
            processes.append(ProcessInput(id=r['id'], arrival_time=r['chegada'],
                                          burst_time=r['execucao'], deadline=dl,
                                          priority=r.get('prioridade')))
        return config, ProcessInputList(processes)
