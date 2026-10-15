from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import yaml
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

OBSERVABLES = ("XX", "YY", "ZZ")


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not config or len(config.get("models", [])) != 3:
        raise ValueError("Config must define exactly three processor models.")
    for model in config["models"]:
        n, ports = model["qubits"], model["ports"]
        if len(ports) != 2 or len(set(ports)) != 2 or any(q < 0 or q >= n for q in ports):
            raise ValueError(f"Invalid ports for {model['id']}")
        if not (0 <= model["ancilla"] < n) or model["ancilla"] in ports:
            raise ValueError(f"Ancilla must be a distinct valid qubit for {model['id']}")
        if any(len(edge) != 2 or edge[0] == edge[1] for edge in model["edges"]):
            raise ValueError(f"Invalid coupling edge for {model['id']}")
    return config


def make_coupling_map(model: dict[str, Any]) -> CouplingMap:
    directed = []
    for a, b in model["edges"]:
        directed.extend([(a, b), (b, a)])
    return CouplingMap(couplinglist=directed, description=model["id"])


def make_noise_model(config: dict[str, Any]) -> NoiseModel:
    params = config["metadata"]["noise"]
    noise = NoiseModel(basis_gates=config["metadata"]["basis_gates"])
    one = depolarizing_error(params["one_qubit_depolarizing"], 1)
    two = depolarizing_error(params["two_qubit_depolarizing"], 2)
    for gate in ("rz", "sx", "x"):
        if gate in config["metadata"]["basis_gates"]:
            noise.add_all_qubit_quantum_error(one, [gate])
    if "cx" in config["metadata"]["basis_gates"]:
        noise.add_all_qubit_quantum_error(two, ["cx"])
    p = params["readout_error"]
    noise.add_all_qubit_readout_error(ReadoutError([[1 - p, p], [p, 1 - p]]))
    return noise


def make_circuit(observable: str, protected: bool) -> QuantumCircuit:
    """Bell preparation, optional ZZ parity measurement, and XX/YY/ZZ readout."""
    qc = QuantumCircuit(3 if protected else 2, 3 if protected else 2)
    qc.h(0)
    qc.cx(0, 1)
    if protected:
        # Measure ZZ using an ancilla initialized to |0>; outcome 0 means +1.
        qc.cx(0, 2)
        qc.cx(1, 2)
    if observable == "XX":
        qc.h(0)
        qc.h(1)
    elif observable == "YY":
        qc.sdg(0)
        qc.sdg(1)
        qc.h(0)
        qc.h(1)
    elif observable != "ZZ":
        raise ValueError(f"Unknown observable: {observable}")
    qc.measure(0, 0)
    qc.measure(1, 1)
    if protected:
        qc.measure(2, 2)
    return qc


def compile_circuit(qc: QuantumCircuit, model: dict[str, Any], config: dict[str, Any]) -> QuantumCircuit:
    layout = [*model["ports"]]
    if qc.num_qubits == 3:
        layout.append(model["ancilla"])
    return transpile(
        qc,
        coupling_map=make_coupling_map(model),
        basis_gates=config["metadata"]["basis_gates"],
        initial_layout=layout,
        optimization_level=config["metadata"].get("optimization_level", 1),
        routing_method=config["metadata"].get("routing_method", "lookahead"),
        seed_transpiler=config["metadata"].get("seed", 1),
    )


def parity_from_key(key: str) -> tuple[int, int, int | None]:
    bits = key.replace(" ", "")
    b0, b1 = int(bits[-1]), int(bits[-2])
    anc = int(bits[-3]) if len(bits) >= 3 else None
    return b0, b1, anc


def summarize_counts(counts: dict[str, int], protected: bool) -> tuple[float, int, int]:
    accepted = total = even = 0
    for key, amount in counts.items():
        total += amount
        b0, b1, anc = parity_from_key(key)
        if protected and anc != 0:
            continue
        accepted += amount
        even += amount * (1 if b0 == b1 else 0)
    if accepted == 0:
        raise RuntimeError("Parity check rejected every shot; fidelity is undefined.")
    # Correlation is +1 for even outcomes and -1 for odd outcomes.
    correlation = (2 * even - accepted) / accepted
    return correlation, accepted, total


def run_case(model: dict[str, Any], config: dict[str, Any], *, noisy: bool,
             protected: bool, shots: int) -> dict[str, Any]:
    noise_model = make_noise_model(config) if noisy else None
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=config["metadata"].get("seed", 1))
    correlations: dict[str, float] = {}
    variances: dict[str, float] = {}
    accepted = total = 0
    circuit_stats: list[dict[str, Any]] = []
    raw_counts: dict[str, dict[str, int]] = {}
    for obs in OBSERVABLES:
        circuit = compile_circuit(make_circuit(obs, protected), model, config)
        result = simulator.run(circuit, shots=shots).result()
        counts = result.get_counts()
        corr, kept, ran = summarize_counts(counts, protected)
        correlations[obs] = corr
        variances[obs] = max(0.0, (1 - corr * corr) / kept)
        accepted += kept
        total += ran
        ops = circuit.count_ops()
        # All listed native two-qubit operations are included in the total.
        twoq = sum(int(n) for name, n in ops.items() if name in {"cx", "cz", "ecr", "iswap", "swap"})
        used_qubits = sorted({circuit.find_bit(q).index for item in circuit.data for q in item.qubits})
        circuit_stats.append({"depth": circuit.depth(), "two_qubit_gates": twoq,
                              "swap_gates": int(ops.get("swap", 0)),
                              "physical_qubits_used": used_qubits})
        raw_counts[obs] = counts
    fidelity = (1 + correlations["XX"] - correlations["YY"] + correlations["ZZ"]) / 4
    sigma = math.sqrt(sum(variances.values())) / 4
    mean_depth = round(sum(x["depth"] for x in circuit_stats) / len(circuit_stats), 2)
    mean_twoq = round(sum(x["two_qubit_gates"] for x in circuit_stats) / len(circuit_stats), 2)
    # The compiled circuits are basis-decomposed, so explicit SWAPs are generally absent.
    # This estimate counts groups of three excess CX operations over the logical CX count.
    mean_swaps = round(max(0, (mean_twoq - (3 if protected else 1)) / 3), 2)
    physical_used = sorted({q for stat in circuit_stats for q in stat["physical_qubits_used"]})
    return {
        "model_id": model["id"], "case": ("ideal" if not noisy else "protected" if protected else "noisy"),
        "fidelity": fidelity, "sigma_f": sigma, "verified_95": fidelity - 2 * sigma > 0.5,
        "correlations": correlations, "depth": mean_depth,
        "two_qubit_gates": mean_twoq, "swap_overhead_estimate": mean_swaps,
        "physical_qubits_used": physical_used,
        "shots": total, "accepted_shots": accepted,
        "acceptance_fraction": accepted / total if total else 0.0,
        "discarded_shots": total - accepted,
        "circuits": circuit_stats, "counts": raw_counts,
    }


def draw_graphs(models: list[dict[str, Any]], output: Path) -> None:
    import matplotlib.pyplot as plt
    import networkx as nx
    output.mkdir(parents=True, exist_ok=True)
    for model in models:
        graph = nx.Graph()
        graph.add_nodes_from(range(model["qubits"]))
        graph.add_edges_from(model["edges"])
        pos = nx.spring_layout(graph, seed=42)
        colors = ["#f59e0b" if n in model["ports"] else "#8bb8d8" if n == model["ancilla"] else "#dce7ef" for n in graph.nodes]
        fig, ax = plt.subplots(figsize=(6, 4.5))
        nx.draw_networkx(graph, pos, ax=ax, node_color=colors, node_size=1100,
                         edge_color="#6b7280", font_size=11, font_weight="bold")
        ax.set_title(f"{model['label']}\nPorts: {model['ports'][0]} and {model['ports'][1]} | ancilla: {model['ancilla']}")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(output / f"{model['id']}-graph.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def write_results(config: dict[str, Any], rows: list[dict[str, Any]], output: Path, shots: int) -> None:
    import csv
    output.mkdir(parents=True, exist_ok=True)
    flat = [{k: v for k, v in row.items() if k not in {"counts", "circuits", "correlations"}} |
            {f"corr_{k}": v for k, v in row["correlations"].items()} for row in rows]
    columns = list(flat[0])
    with (output / "results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(flat)
    (output / "results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (output / "run_metadata.json").write_text(json.dumps({
        "definition_status": config["metadata"].get("definition_status", "UNSPECIFIED"),
        "seed": config["metadata"].get("seed"), "shots_per_setting": shots,
        "models": config["models"], "noise": config["metadata"]["noise"],
        "note": "Replace starter definitions with the organizer's common definitions before official comparison."
    }, indent=2), encoding="utf-8")
    rows_by_model = {m["id"]: {r["case"]: r for r in rows if r["model_id"] == m["id"]} for m in config["models"]}
    lines = ["# Nine-case comparison", "", "Starter-profile runs are illustrative until official definitions are entered.", "",
             "| Model | Case | Fidelity ± σ | Verified (F−2σ > 0.5) | Depth | 2Q gates | SWAP estimate | Qubits | Accepted | Yield | Discarded |",
             "|---|---|---:|:---:|---:|---:|---:|---|---:|---:|---:|"]
    for model in config["models"]:
        for case in ("ideal", "noisy", "protected"):
            row = rows_by_model[model["id"]][case]
            lines.append(f"| {model['label']} | {case} | {row['fidelity']:.4f} ± {row['sigma_f']:.4f} | {'Yes' if row['verified_95'] else 'No'} | {row['depth']} | {row['two_qubit_gates']} | {row['swap_overhead_estimate']} | {row['physical_qubits_used']} | {row['accepted_shots']} | {row['acceptance_fraction']:.3f} | {row['discarded_shots']} |")
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
