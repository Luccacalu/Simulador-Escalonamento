"""Adaptador de entrada (linha de comando, argparse da biblioteca padrão)."""
import argparse
import os
import sys
import time

from app import ALL_ALGORITHMS, Simulator
from core.inbound_ports import SimulationResult
from external.image_generator import ImageGenerator
from external.json_reader import JsonReader
from external.log_writer import LogWriter, format_stamp


def _v(x):
    return '-' if x is None else x


def format_table(r: SimulationResult) -> str:
    head = ['id', 'chegada', 'execucao', 'deadline', 'prioridade', 'inicio', 'termino',
            'espera', 'turnaround', 'deadline_ok?']
    rows = [[m.pid, m.arrival_time, m.burst_time, _v(m.deadline), _v(m.priority), m.start_time,
             m.completion_time, m.waiting_time, m.turnaround_time,
             '-' if m.deadline_ok is None else ('sim' if m.deadline_ok else 'NAO (estourou)')]
            for m in r.table]
    w = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
    line = lambda c: '  '.join(str(x).rjust(n) for x, n in zip(c, w))
    return '\n'.join([line(head)] + [line(x) for x in rows])


def format_summary(r: SimulationResult) -> str:
    m = r.metrics
    return '\n'.join([
        f'Turnaround médio ........ {m.average_turnaround_time:.2f}   (= "tempo médio de resposta")',
        f'Espera média ............ {m.average_waiting_time:.2f}',
        f'Resposta média (inicio) . {m.average_response_time:.2f}',
        f'Deadlines estourados .... {m.lost_deadlines}',
        f'Throughput .............. {m.throughput:.4f} processos/u.t.',
        f'CPU ociosa .............. {m.idle_time} u.t. ({m.idle_percent:.1f}%)',
        f'Sobrecarga de contexto .. {m.overhead_time} u.t. ({m.overhead_percent:.1f}%)',
        f'Trocas de contexto ...... {m.total_preemptions}',
        f'Tempo total ............. {m.total_time} u.t.',
    ])


def format_comparison(results: list[SimulationResult]) -> str:
    head = ['algoritmo', 'turnaround', 'espera', 'resposta', 'estouros', 'throughput',
            'ocioso%', 'sobrecarga%', 'trocas']
    rows = [[r.algorithm, f'{r.metrics.average_turnaround_time:.2f}',
             f'{r.metrics.average_waiting_time:.2f}', f'{r.metrics.average_response_time:.2f}',
             r.metrics.lost_deadlines, f'{r.metrics.throughput:.4f}',
             f'{r.metrics.idle_percent:.1f}', f'{r.metrics.overhead_percent:.1f}',
             r.metrics.total_preemptions] for r in results]
    w = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
    line = lambda c: '  '.join(str(x).rjust(n) for x, n in zip(c, w))
    return '\n'.join([line(head)] + [line(x) for x in rows])


def _suffix(path: str, alg: str, multi: bool) -> str:
    if not multi:
        return path
    base, ext = os.path.splitext(path)
    return f'{base}_{alg}{ext}'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog='simso', description='Simulador de escalonamento de processos')
    ap.add_argument('--alg', required=True,
                    help='FCFS|SJF|RR|PRIORITY|EDF|CFS|AUTORAL|ALL (FIFO = FCFS)')
    ap.add_argument('--input', required=True, help='arquivo JSON de entrada')
    ap.add_argument('--gantt', help='PNG do gráfico de Gantt (com ALL, vira caso_ALG.png)')
    ap.add_argument('--log', help='arquivo de log da linha do tempo')
    ap.add_argument('--seed', type=int, help='seed (determinismo)')
    ap.add_argument('--quantum', type=int, help='sobrescreve o quantum do JSON')
    ap.add_argument('--overhead', type=int, help='sobrescreve sobrecarga_contexto do JSON')
    ap.add_argument('--delay', type=int, default=0,
                    help='modo passo-a-passo: atraso em ms entre eventos (ex.: 150)')
    args = ap.parse_args(argv)

    simulator = Simulator()
    algs = ALL_ALGORITHMS if args.alg.upper() == 'ALL' else [args.alg.upper()]
    results = []
    for name in algs:
        try:
            config, processes = JsonReader().read(args.input)  # lê de novo: a lista é consumida
            if args.quantum is not None:
                if args.quantum <= 0:
                    raise ValueError('quantum deve ser > 0')
                config.quantum = args.quantum
            if args.overhead is not None:
                if args.overhead < 0:
                    raise ValueError('sobrecarga_contexto deve ser >= 0')
                config.overhead = args.overhead
            if args.seed is not None:
                config.seed = args.seed
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f'Erro ({name}): {e}', file=sys.stderr)
            return 1
        try:
            r = simulator.run(name, config, processes)
        except ValueError as e:
            print(f'Erro ({name}): {e}', file=sys.stderr)
            return 1
        results.append(r)

        if args.delay:
            for s in r.timestamps:
                print(format_stamp(s), flush=True)
                time.sleep(args.delay / 1000)
        report = f'=== {r.algorithm} ===\n{format_table(r)}\n\n{format_summary(r)}'
        print(('\n' if not args.delay else '') + report + '\n')
        if args.gantt:
            ImageGenerator().save(r.gantt, _suffix(args.gantt, name, len(algs) > 1))
        if args.log:
            LogWriter().write(_suffix(args.log, name, len(algs) > 1), r.timestamps, report)

    if len(results) > 1:
        print('=== COMPARAÇÃO ===\n' + format_comparison(results))
    return 0
