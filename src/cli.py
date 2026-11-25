"""Linha de comando.

Exemplo:
  python main.py --alg CFS --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log --seed 42 --delay 150
  python main.py --alg ALL --input casos/caso1.json --gantt out/caso1.png      (roda todos e compara)
"""
import argparse
import os
import random
import sys
import time

from algorithms import ALGORITHMS, make_algorithm
from simulator import simulate
from metrics import individual_metrics, global_metrics
from io_utils import load_input, format_table, format_summary, write_log, describe_slot
from gantt import draw_gantt


def _with_suffix(path: str, alg: str) -> str:
    base, ext = os.path.splitext(path)
    return f"{base}_{alg.lower()}{ext}"


def _ensure_dir(path: str | None) -> None:
    if path and os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)


def run_one(cfg, alg_name, gantt, log, delay_ms, many):
    alg = make_algorithm(alg_name, cfg.quantum)
    timeline, finished = simulate(cfg.processes, alg, cfg.overhead)
    table = individual_metrics(finished)
    summary = global_metrics(table, timeline, cfg.overhead)

    print(f"\n===== {alg.name} (quantum={cfg.quantum}, sobrecarga={cfg.overhead}) =====")
    if delay_ms:  # modo passo a passo
        for s in timeline:
            print(describe_slot(s))
            time.sleep(delay_ms / 1000)
    print(format_table(table))
    print()
    print(format_summary(summary))

    if gantt:
        out = _with_suffix(gantt, alg.name) if many else gantt
        _ensure_dir(out)
        draw_gantt(timeline, finished, f"Gantt - {alg.name}", out)
        print(f"Gantt salvo em {out}")
    if log:
        out = _with_suffix(log, alg.name) if many else log
        _ensure_dir(out)
        write_log(out, alg.name, timeline, table, summary)
        print(f"Log salvo em {out}")
    return alg.name, summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="simso", description="Simulador de escalonamento de processos")
    ap.add_argument("--alg", required=True, help=f"{' | '.join(ALGORITHMS)} | ALL")
    ap.add_argument("--input", required=True, help="arquivo JSON de entrada")
    ap.add_argument("--gantt", help="caminho do PNG do Gantt")
    ap.add_argument("--log", help="caminho do arquivo de log")
    ap.add_argument("--seed", type=int, help="semente (só importa no módulo bônus de memória virtual)")
    ap.add_argument("--delay", type=int, default=0, help="atraso em ms entre eventos (modo passo a passo)")
    args = ap.parse_args(argv)

    try:
        cfg = load_input(args.input)
        random.seed(args.seed if args.seed is not None else cfg.seed)
        names = list(ALGORITHMS) if args.alg.upper() == "ALL" else [args.alg.upper()]
        results = [run_one(cfg, n, args.gantt, args.log, args.delay, many=len(names) > 1) for n in names]
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    if len(results) > 1:
        print("\n===== COMPARAÇÃO =====")
        print(f"{'alg':9}{'turnaround':>11}{'espera':>9}{'resposta':>10}{'deadl.perd':>11}{'throughput':>11}{'ociosa%':>9}{'trocas':>8}")
        for name, g in results:
            print(f"{name:9}{g.average_turnaround_time:11.2f}{g.average_waiting_time:9.2f}"
                    f"{g.average_response_time:10.2f}{g.lost_deadlines:11d}{g.throughput:11.4f}"
                    f"{g.idle_percent:9.1f}{g.context_switches:8d}")
    return 0
