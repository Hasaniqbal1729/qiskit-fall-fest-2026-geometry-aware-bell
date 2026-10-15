from __future__ import annotations
import argparse
from pathlib import Path
from .core import draw_graphs, load_config, run_case, write_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the three-model Bell geometry benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run all nine benchmark cases")
    run.add_argument("--config", default="config/benchmark.yaml")
    run.add_argument("--output", default="results")
    run.add_argument("--shots", type=int, default=None)
    args = parser.parse_args()
    if args.command == "run":
        config = load_config(args.config)
        shots = args.shots or config["metadata"].get("shots", 4096)
        output = Path(args.output)
        figures = output.parent / "figures" if output.name == "results" else output / "figures"
        draw_graphs(config["models"], figures)
        rows = []
        for model in config["models"]:
            for noisy, protected in ((False, False), (True, False), (True, True)):
                result = run_case(model, config, noisy=noisy, protected=protected, shots=shots)
                rows.append(result)
                print(f"{model['id']:24s} {result['case']:9s} F={result['fidelity']:.4f} ± {result['sigma_f']:.4f} yield={result['acceptance_fraction']:.3f}")
        write_results(config, rows, output, shots)
        print(f"Wrote comparison to {output / 'comparison.md'}")

if __name__ == "__main__":
    main()
