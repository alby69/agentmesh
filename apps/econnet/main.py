import argparse
import json
import logging
from pathlib import Path

from econnet.simulation.engine import SimulationEngine
from econnet.visualization.plots import (
    plot_price_history,
    plot_emotional_state,
    plot_budget_distribution,
    plot_crash_detection,
    plot_graeber_metrics,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("econnet.main")


def main():
    parser = argparse.ArgumentParser(description="EconNet — Economic Simulator (ABM + AI)")
    parser.add_argument("--ticks", type=int, default=200, help="Number of simulation ticks (default: 200)")
    parser.add_argument("--consumers", type=int, default=100, help="Number of consumer agents (default: 100)")
    parser.add_argument("--producers", type=int, default=10, help="Number of producer agents (default: 10)")
    parser.add_argument("--budget", type=float, default=100.0, help="Base consumer budget (default: 100)")
    parser.add_argument("--price", type=float, default=10.0, help="Initial market price (default: 10)")
    parser.add_argument("--network", choices=["random", "small-world", "scale-free"], default="small-world", help="Social network topology")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--visualize", action="store_true", help="Generate plots after simulation")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file for tick log")
    parser.add_argument("--output-dir", type=str, default="apps/econnet/output", help="Directory for output files (default: apps/econnet/output)")
    parser.add_argument("--verbose", action="store_true", help="Print progress every 50 ticks")

    # Graeberian Command Line Arguments
    parser.add_argument("--graeber", action="store_true", help="Enable Graeberian economics extensions")
    parser.add_argument("--initial-peace", type=float, default=1.0, help="Initial Graeberian social peace/trust level (default: 1.0)")
    parser.add_argument("--tribute-rate", type=float, default=0.05, help="Rate of tribute/charity based on budget (default: 0.05)")

    args = parser.parse_args()

    # Pass Graeber config to the engine
    config = {
        "graeber": args.graeber,
        "initial_peace": args.initial_peace,
        "tribute_rate": args.tribute_rate,
    }

    engine = SimulationEngine(config=config, seed=args.seed)
    engine.setup(
        num_consumers=args.consumers,
        num_producers=args.producers,
        consumer_budget=args.budget,
        initial_price=args.price,
        network_type=args.network,
    )

    print(f"\n{'='*60}")
    print("ECONNET — Economic Agent-Based Simulator")
    print(f"{'='*60}")
    print(f"Consumers:    {args.consumers}")
    print(f"Producers:    {args.producers}")
    print(f"Network:      {args.network}")
    print(f"Ticks:        {args.ticks}")
    print(f"Seed:         {args.seed}")
    print(f"Graeber Mode: {args.graeber}")
    if args.graeber:
        print(f"  - Initial Social Peace: {args.initial_peace}")
        print(f"  - Tribute Rate:         {args.tribute_rate}")
    print(f"{'='*60}\n")

    tick_log = engine.run(max_ticks=args.ticks, verbose=args.verbose)

    summary = engine.get_summary()
    print(f"\n{'='*60}")
    print("SIMULATION SUMMARY")
    print(f"{'='*60}")
    print(f"Ticks executed:   {summary['ticks']}")
    print(f"Network edges:    {summary['network_edges']}")
    print(f"Network density:  {summary['network_density']}")
    print(f"Avg clustering:   {summary['avg_clustering']}")
    print(f"Current price:    {summary['market'].get('current_price', 0):.2f}")
    print(f"Avg price:        {summary['market'].get('avg_price', 0):.2f}")
    print(f"Avg volume:       {summary['market'].get('avg_volume', 0):.1f}")
    print(f"Total txns:       {summary['market'].get('total_transactions', 0)}")
    print(f"Price volatility: {summary['market'].get('price_volatility', 0):.4f}")

    if summary.get("graeber_active"):
        print(f"\n{'*'*15} GRAEBERIAN METRICS {'*'*15}")
        print(f"Final Social Peace:       {summary['social_peace_final']:.3f}")
        print(f"Mutual Aid Counts:        {summary['total_mutual_aid_count']}")
        print(f"Mutual Aid Volume:        {summary['total_mutual_aid_volume']:.2f}")
        print(f"Tributes Paid (Hierarchy): {summary['total_tributes_paid']:.2f}")
        print(f"Charity Paid (Hierarchy):  {summary['total_charity_paid']:.2f}")
        print(f"Credit Sales Volume:      {summary['total_credit_sales_volume']:.2f}")
        print(f"Debt Defaults Count:      {summary['total_defaults_count']}")
        print(f"Defaulted Losses:         {summary['total_defaulted_losses']:.2f}")

    print(f"{'='*60}\n")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(tick_log, f, indent=2, ensure_ascii=False)
        print(f"Tick log saved to: {args.output}")

    if args.visualize:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        prefix = "econnet_sim"
        paths = {
            "price": out_dir / f"{prefix}_price.png",
            "emotions": out_dir / f"{prefix}_emotions.png",
            "budgets": out_dir / f"{prefix}_budgets.png",
            "crashes": out_dir / f"{prefix}_crashes.png",
            "graeber": out_dir / f"{prefix}_graeber.png",
        }
        print("Generating plots...")
        plot_price_history(tick_log, output_path=str(paths["price"]))
        plot_emotional_state(tick_log, output_path=str(paths["emotions"]))
        plot_budget_distribution(engine.get_agent_states(), output_path=str(paths["budgets"]))
        plot_crash_detection(tick_log, output_path=str(paths["crashes"]))
        if args.graeber:
            plot_graeber_metrics(tick_log, output_path=str(paths["graeber"]))
        print(f"Plots saved to {out_dir}/:")
        for name, p in paths.items():
            if name == "graeber" and not args.graeber:
                continue
            print(f"  - {p.name}")


if __name__ == "__main__":
    main()
