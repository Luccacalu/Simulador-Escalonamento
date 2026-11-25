"""Gráfico de Gantt (matplotlib): uma linha por processo.

Cores:
    verde    -> execução
    vermelho -> sobrecarga de contexto (desenhada na linha do processo que saiu da CPU)
    cinza    -> execução que ocorreu depois do deadline (estouro)
    linha vertical preta -> deadline absoluto (chegada + deadline) do processo
    Faixa amarela clara no fundo -> CPU ociosa.
"""
import matplotlib

matplotlib.use("Agg")  # sem janela: só gera o arquivo
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from models import Process, Slot

GREEN, RED, GRAY, YELLOW, IDLE = "#2e9e4f", "#d64545", "#8c8c8c", "#f5c518", "#e3e8f0"


def draw_gantt(timeline: list[Slot], processes: list[Process], title: str, path: str) -> None:
    order = sorted(processes, key=lambda p: (p.arrival_time, p.id))
    row = {p.id: i for i, p in enumerate(order)}
    by_id = {p.id: p for p in order}
    total = len(timeline)

    fig, ax = plt.subplots(figsize=(max(8.0, total * 0.32), 1.0 + 0.7 * len(order)))

    for s in timeline:
        if s.kind == "idle":
            ax.axvspan(s.t, s.t + 1, color=IDLE, zorder=0)
            continue
        y = row[s.pid]
        if s.kind == "overhead":
            color = RED
        else:
            dl = by_id[s.pid].new_deadline
            color = GRAY if dl is not None and s.t + 1 > dl else GREEN
        ax.barh(y, 1, left=s.t, height=0.6, color=color, edgecolor="white", linewidth=0.6, zorder=2)

    # espera: processo já chegou, ainda não terminou e não está executando nem em sobrecarga
    busy = {(s.pid, s.t) for s in timeline if s.kind in ("exec", "overhead")}
    for p in order:
        for t in range(p.arrival_time, p.completion_time):
            if (p.id, t) not in busy:
                ax.barh(row[p.id], 1, left=t, height=0.6, color=YELLOW, edgecolor="white", linewidth=0.6, zorder=2)

    for p in order:
        if p.new_deadline is not None:
            y = row[p.id]
            ax.plot([p.new_deadline, p.new_deadline], [y - 0.42, y + 0.42], color="black", linewidth=1.8, zorder=3)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([p.id for p in order])
    ax.invert_yaxis()
    ax.set_xlim(0, max(total, max((p.new_deadline or 0) for p in order)) + 0.5)
    ax.set_xticks(range(0, int(ax.get_xlim()[1]) + 1, 2))
    ax.set_xlabel("tempo (u.t.)")
    ax.set_title(title)
    ax.grid(axis="x", linestyle=":", alpha=0.4, zorder=1)
    ax.legend(
        handles=[
            Patch(color=GREEN, label="execução"),
            Patch(color=RED, label="sobrecarga de contexto"),
            Patch(color=GRAY, label="estouro de deadline"),
            Patch(color=IDLE, label="CPU ociosa"),
            Patch(color=YELLOW, label="espera"),
            Line2D([0], [0], color="black", linewidth=2, label="deadline"),
        ],
        loc="upper center", bbox_to_anchor=(0.5, -0.5 if len(order) <= 3 else -0.25), ncol=5, frameon=False,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
