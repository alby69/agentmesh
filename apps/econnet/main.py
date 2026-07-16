import argparse
import json
import logging

from econnet.simulation.engine import SimulationEngine
from econnet.visualization.plots import (
    plot_price_history,
    plot_emotional_state,
    plot_budget_distribution,
    plot_crash_detection,
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
    parser.add_argument("--verbose", action="store_true", help="Print progress every 50 ticks")

    args = parser.parse_args()

    engine = SimulationEngine(seed=args.seed)
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
    print(f"{'='*60}\n")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(tick_log, f, indent=2, ensure_ascii=False)
        print(f"Tick log saved to: {args.output}")

    if args.visualize:
        print("Generating plots...")
        prefix = "econnet_sim"
        plot_price_history(tick_log, output_path=f"{prefix}_price.png")
        plot_emotional_state(tick_log, output_path=f"{prefix}_emotions.png")
        plot_budget_distribution(engine.get_agent_states(), output_path=f"{prefix}_budgets.png")
        plot_crash_detection(tick_log, output_path=f"{prefix}_crashes.png")
        print(f"Plots saved: {prefix}_price.png, {prefix}_emotions.png, {prefix}_budgets.png, {prefix}_crashes.png")


if __name__ == "__main__":
    main()
