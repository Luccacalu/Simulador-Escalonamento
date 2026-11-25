# Simulador de Escalonamento (Sistemas Operacionais)

Simulador de eventos discretos para CPU single-core com 7 algoritmos, Gantt, tabela final e métricas.

## Uso

```
pip install -r requirements.txt
python main.py --alg CFS --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log --seed 42 --delay 150
python main.py --alg ALL --input casos/caso_professor.json --gantt out/prof.png   # todos + comparação
python -m pytest
```

`--alg`: FCFS, SJF, RR, PRIORITY, EDF, CFS, AGING (autoral) ou ALL. `--delay` (ms) ativa o passo a passo.

## Estrutura

| Arquivo | Papel |
|---|---|
| `src/models.py` | `Process` (dados + estado) e `Slot` (1 u.t. da linha do tempo: exec / overhead / idle) |
| `src/algorithms.py` | um algoritmo por classe (`pick` = quem executa, `slice_for` = por quanto tempo) |
| `src/simulator.py` | laço guiado por tempo (1 passo = 1 u.t.); sobrecarga, ociosidade e fila de prontos |
| `src/metrics.py` | tabela individual e resumo global |
| `src/gantt.py` | Gantt em matplotlib |
| `src/io_utils.py` | leitura do JSON, log, tabela e resumo |
| `src/cli.py`, `main.py` | linha de comando |
| `tests/` | exemplo de questão do professor, casos públicos, invariantes de todos os algoritmos |

## Decisões de projeto (para o relatório)

- **Deadline**: no JSON é relativo; o instante limite é `chegada + deadline`. Esse valor ordena o EDF,
  decide `deadline_ok` (`término <= chegada + deadline`) e posiciona a linha do Gantt.
- **Sobrecarga**: não preemptivos (FCFS, SJF) não pagam. Nos preemptivos com quantum (RR, PRIORITY, EDF, AGING)
  paga-se ao fim de cada quantum se o processo não terminou, mesmo que o mesmo continue. No CFS só se paga ao trocar de processo. Término de processo e
  primeiro despacho não pagam. No Gantt, a sobrecarga fica na linha do processo que saiu.
- **Preempção** em RR/PRIORITY/EDF/AGING é avaliada nas fronteiras de quantum.
- **Fila de prontos**: ao fim do quantum, chegadas até esse instante
  entram na fila; o processo preemptado paga a sobrecarga fora da fila; chegadas durante a sobrecarga (inclusive no
  instante em que ela termina) entram; só então o preemptado volta para o fim da fila.
- **Métricas**: `turnaround = término - chegada`, `espera = turnaround - execução`, `resposta = início - chegada`.
  O "tempo médio de resposta" da resolução equivale ao turnaround médio.
  `% ociosa` inclui sobrecarga (o PDF trata sobrecarga como CPU ociosa); `ociosa` e `sobrecarga` também são reportadas separadas.
- **CFS-Sim**: `vruntime = tempo atual` na chegada, `+= Δt * 1.25^(prioridade-1)`, menor vruntime executa, fatia de
  1 u.t. (a preempção ocorre assim que outro processo tem vruntime menor).
- **AGING (autoral)**: SRTF com envelhecimento. Pontuação = restante - 0,5 × tempo esperando; menor pontuação executa.
  Mantém o bom turnaround do SRTF e evita inanição de processos longos.
- Bônus de memória virtual (`num_paginas`, `custo_disco`): não implementado.
