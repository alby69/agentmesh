from typing import Any, Dict, List, Optional
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def plot_price_history(
    tick_log: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    if not tick_log:
        return

    ticks = [d["tick"] for d in tick_log]
    prices = [d["price"] for d in tick_log]
    volumes = [d.get("volume", 0) for d in tick_log]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle("EconNet — Andamento Mercato", fontsize=14, fontweight="bold")

    ax1.plot(ticks, prices, color="#2196F3", linewidth=1.2, label="Prezzo")
    ax1.set_ylabel("Prezzo", fontsize=11)
    ax1.set_title("Prezzo di Mercato nel Tempo")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

    ax2.bar(ticks, volumes, color="#4CAF50", alpha=0.7, width=1.0)
    ax2.set_xlabel("Tick", fontsize=11)
    ax2.set_ylabel("Volume", fontsize=11)
    ax2.set_title("Volume di Transazioni")
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_emotional_state(
    tick_log: List[Dict[str, Any]],
    consumer_histories: Optional[List[Dict[str, Any]]] = None,
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    if not tick_log:
        return

    ticks = [d["tick"] for d in tick_log]
    satisfactions = [d.get("avg_consumer_satisfaction", 0.5) for d in tick_log]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(ticks, satisfactions, color="#FF9800", linewidth=1.2, label="Soddisfazione Media")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Neutro")
    ax.set_xlabel("Tick", fontsize=11)
    ax.set_ylabel("Soddisfazione Media", fontsize=11)
    ax.set_title("EconNet — Stato Emotivo Medio Consumatori")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_budget_distribution(
    agent_states: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    budgets = [a["budget"] for a in agent_states]
    types = [a.get("type", "unknown") for a in agent_states]

    fig, ax = plt.subplots(figsize=(12, 5))

    consumer_budgets = [b for b, t in zip(budgets, types) if t == "consumer"]
    producer_budgets = [b for b, t in zip(budgets, types) if t == "producer"]

    if consumer_budgets:
        ax.hist(consumer_budgets, bins=30, color="#2196F3", alpha=0.7, label="Consumatori")
    if producer_budgets:
        ax.hist(producer_budgets, bins=20, color="#F44336", alpha=0.7, label="Produttori")

    ax.set_xlabel("Budget", fontsize=11)
    ax.set_ylabel("Numero Agenti", fontsize=11)
    ax.set_title("EconNet — Distribuzione Budget")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_crash_detection(
    tick_log: List[Dict[str, Any]],
    threshold: float = -0.05,
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    if len(tick_log) < 2:
        return

    ticks = [d["tick"] for d in tick_log]
    prices = [d["price"] for d in tick_log]

    returns = [0.0]
    for i in range(1, len(prices)):
        if prices[i - 1] != 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])
        else:
            returns.append(0.0)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(ticks, returns, color="#607D8B", linewidth=0.8, label="Rendimento")
    ax.axhline(y=threshold, color="red", linestyle="--", alpha=0.7, label=f"Soglia crash ({threshold})")

    crash_ticks = [t for t, r in zip(ticks, returns) if r <= threshold]
    if crash_ticks:
        ax.scatter(crash_ticks, [returns[ticks.index(t)] for t in crash_ticks],
                   color="red", s=50, zorder=5, label=f"Crash ({len(crash_ticks)})")

    ax.set_xlabel("Tick", fontsize=11)
    ax.set_ylabel("Rendimento", fontsize=11)
    ax.set_title("EconNet — Rilevamento Crash")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_graeber_metrics(
    tick_log: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    if not tick_log or not tick_log[0].get("graeber", False):
        return

    ticks = [d["tick"] for d in tick_log]
    peace = [d.get("social_peace", 1.0) for d in tick_log]
    debts = [d.get("total_debt", 0.0) for d in tick_log]
    mutual_aid = [d.get("mutual_aid_count", 0) for d in tick_log]
    defaults = [d.get("defaults_count", 0) for d in tick_log]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("EconNet — Graeberian Co-evolution Dynamics", fontsize=14, fontweight="bold")

    # Plot 1: Social Peace (Trust Cycle)
    ax1.plot(ticks, peace, color="#9C27B0", linewidth=1.5, label="Pace Sociale / Fiducia")
    ax1.axhline(y=0.4, color="red", linestyle="--", alpha=0.5, label="Soglia Squeeze di Credito")
    ax1.set_ylabel("Livello Fiducia", fontsize=11)
    ax1.set_title("Evoluzione della Fiducia Sociale (Pace Sociale)")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.05)

    # Plot 2: Virtual Debt vs. Cash defaults
    ax2.plot(ticks, debts, color="#E91E63", linewidth=1.2, label="Debito Totale Pendente")
    ax2.set_ylabel("Volume Debito", fontsize=11)
    ax2.set_title("Co-evoluzione del Debito Virtuale")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Dual axis for defaults count
    ax2_twin = ax2.twinx()
    ax2_twin.plot(ticks, defaults, color="#F44336", linestyle=":", linewidth=1.5, label="Inadempienze (Defaults)")
    ax2_twin.set_ylabel("Numero Fallimenti", fontsize=11, color="#F44336")
    ax2_twin.tick_params(axis='y', labelcolor="#F44336")
    ax2_twin.legend(loc="upper right")

    # Plot 3: Baseline Communism (Mutual Aid)
    ax3.plot(ticks, mutual_aid, color="#4CAF50", linewidth=1.5, label="Aiuto Mutuo (Comunismo di Base)")
    ax3.set_xlabel("Tick", fontsize=11)
    ax3.set_ylabel("Conteggio Regali", fontsize=11)
    ax3.set_title("Frequenza Aiuto Mutuo (Comunismo di Base)")
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))

    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
