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
        config = SimulationConfig(
            quantum=raw.get('quantum', 2),
            overhead=raw.get('sobrecarga_contexto', 0),
            seed=raw.get('seed'),
            disk_cost=raw.get('custo_disco', 0),
        )
        relative = raw.get('deadline_relativo', False)
        processes = []
        for r in raw['processos']:
            dl = r.get('deadline')
            if dl is not None and not relative:
                dl -= r['chegada']
            processes.append(ProcessInput(id=r['id'], arrival_time=r['chegada'],
                                          burst_time=r['execucao'], deadline=dl,
                                          priority=r.get('prioridade')))
        return config, ProcessInputList(processes)
