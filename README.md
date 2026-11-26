# Simulador de Escalonamento (Sistemas Operacionais)

Simulador de eventos discretos (CPU single-core) com FCFS, SJF, Round-Robin, Prioridades,
EDF, CFS-Sim e um algoritmo autoral. Gera Gantt (PNG), log, tabela final e resumo.

## Equipe

| Nome | Usuário GitHub |
| --- | --- |
| Lucca Giovanni Lobo Gonçalves | [Luccacalu](https://github.com/Luccacalu) |
| Gabriel Silva Carvalho | [gbrcarvalho](https://github.com/gbrcarvalho) |
| Davi Antoniassi | [daantoniassi](https://github.com/daantoniassi) |
| Rafael Souza Franco | [RafaelSF-br](https://github.com/RafaelSF-br) |

## Uso

```bash
pip install -r requirements.txt            # só Pillow (e pytest para os testes)
python main.py --alg CFS --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log --seed 42 --delay 150
python main.py --alg ALL --input casos/caso1.json --gantt out/caso1.png   # todos + tabela comparativa
python -m pytest                                                          # testes
```

`--alg`: `FCFS|FIFO|SJF|RR|PRIORITY|EDF|CFS|AUTORAL|ALL`. Também: `--quantum`, `--overhead`, `--seed`.
`--delay N` = modo passo-a-passo (N ms entre eventos). Com `ALL` os arquivos ganham o sufixo `_ALG`.

## JSON de entrada

Como no enunciado (`quantum`, `sobrecarga_contexto`, `custo_disco`, `seed`, `processos[]` com
`id, chegada, execucao, deadline, prioridade`). `deadline` é **absoluto** (enunciado). Para a
resolução com deadline relativo à chegada use `"deadline_relativo": true`.
`num_paginas`/`custo_disco` (bônus de memória virtual) são aceitos e ignorados.

## Arquitetura Hexagonal

```
src/core/            domínio (sem I/O)
  process/           ProcessInput (imutável), ProcessInputList, ReadyProcess (+Deadline/Priority/Fair)
  engine/            Engine, ProcessExecutor, SchedulingAlgorithm, algorithms/*
  gantt/             Timestamp, ExecutionLogger, GanttChartGenerator, GanttChartData
  metrics/           IndividualMetrics, GlobalMetrics, GlobalMetricsCalculator
  inbound_ports.py   porta de entrada (SimulationUseCase, SimulationConfig/Result)
  outbound_ports.py  portas de saída (InputReader, LogWriter, ImageGenerator)
src/app.py           Simulator: liga domínio às portas
src/external/        adaptadores: cli, json_reader, log_writer, image_generator (Pillow)
```

## Convenções

- Sobrecarga de chaveamento cobrada ao fim de **toda fatia em que o processo não termina**,
  inclusive se ele continuar (ex.: `(A,A)`); quando o processo termina, o próximo começa sem sobrecarga.
- FCFS/SJF são não preemptivos (fatia = burst), logo sem sobrecarga.
- RR/Prioridades/EDF/CFS/Autoral decidem **só nas fronteiras de quantum**.
- Fila do RR: quem chega **até o fim da sobrecarga** entra antes do preemptado, que vai ao fim da fila.
- `espera = turnaround - execução`; `turnaround = término - chegada`.
  O "tempo médio de resposta" = **turnaround médio**; o campo `resposta`
  (início − chegada) também é reportado.
- CFS-Sim: `vruntime = tempo de chegada`; `+= Δt * 1.25^(prioridade-1)`; executa o menor vruntime;
  fatia granular = `quantum`.
- Autoral: **HRRN preemptivo** — razão `(espera+restante)/restante` (curtos primeiro, sem inanição).
- Gantt: verde = execução, vermelho = sobrecarga (na linha de quem saiu), amarelo = processo
  pronto aguardando CPU, cinza = execução após o deadline, linha azul vertical = deadline absoluto.

## Validação

`tests/test_algorithms.py` reproduz questões antigas  (FIFO 7,75; SJF 7,25; RR 13,75;
EDF 11,5 sem deadlines perdidos) e checa invariantes de todos os algoritmos (tempo contínuo,
burst executado, CPU ociosa, métricas).

## Pendências do trabalho 

Bônus de memória virtual não implementado.
