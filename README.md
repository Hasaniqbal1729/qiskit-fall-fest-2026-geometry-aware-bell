# Geometry-aware Bell benchmark — Basic Track

A reproducible Qiskit study of Bell-pair preparation and a ZZ parity check across three processor geometries. The workflow covers ideal, noisy, and noisy-with-protection cases; estimates fidelity from XX, YY, and ZZ; records uncertainty, circuit cost, routing, qubit use, and post-selection yield; and writes graph diagrams and a nine-case results table.

> **Organizer definitions required:** the supplied challenge PDF refers to common definitions announced separately, but this copy does not contain their exact graphs, ports, basis gates, noise parameters, or shot count. `config/benchmark.yaml` therefore contains **illustrative starter profiles**, not official benchmark definitions. Replace every field marked `OFFICIAL`/starter before making scientific or hackathon claims. Results generated from starter values are examples only.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
bellbench run --config config/benchmark.yaml --output results --shots 4096
```

Open `report/report.md` and `presentation/walkthrough.md` after the run. Graph images and CSV/JSON results are created under the output directory. Simulation is local; no IBM account is required. The contemporary profile is a frozen, five-qubit teaching profile so all three models share one transparent workflow. Replace it with the organizer-designated fake backend snapshot or device configuration when those details are available.

## What it measures

For each processor profile, the tool compiles the logical H(0), CX(0,1) Bell circuit with the two logical data qubits placed on the designated ports. It runs three readout settings: direct ZZ, H⊗H before readout for XX, and S†H on both ports for YY. The Bell fidelity and independent-shot uncertainty are

`F = (1 + <XX> - <YY> + <ZZ>)/4`

`σF = sqrt(σXX² + σYY² + σZZ²)/4`, where `σPP = sqrt((1 - <PP>²)/N)`.

A result is marked verified only when `F - 2σF > 0.5`. Protection uses an ancilla to measure ZZ parity and retains ancilla outcome 0. The table reports conditional fidelity and the accepted-shot fraction alongside added circuit cost. A ZZ check detects single X/Y errors and does not detect Z errors.

## Reproducibility and interpretation

- Fixed seed and shot count are recorded in `run_metadata.json`.
- The three starter profiles use the same gate set and noise parameters to make the graph effect easier to inspect. This is an optional controlled comparison, not the official models.
- The standard nine-case grid is always emitted: 3 models × ideal/noisy/protected.
- Counts and transpiled circuit summaries are saved for auditability.
- SWAP count is reported as an estimate from excess two-qubit gates relative to the logical circuit and documented in the report; physical coupling and compilation can alter the decomposition.
- No result is hard-coded into the report. Fill the final interpretation and design recommendation from the output files.

## Repository map

- `config/benchmark.yaml` — editable model definitions and noise assumptions.
- `src/bellbench/` — circuit construction, simulation, statistics, diagrams, and CLI.
- `report/report.md` — report structure with evidence prompts.
- `presentation/walkthrough.md` — 5–7 minute recorded-presentation script and shot list.
- `results/` — generated CSV/JSON outputs (initially empty).
- `figures/` — generated coupling-map plots (initially empty).

## Submission checklist

1. Replace the starter profiles with the organizer's exact definitions and verify all three port mappings.
2. Run the benchmark and review all nine cases and their uncertainty/yield.
3. Complete `report/report.md` using the actual output; include limits and a result-supported recommendation.
4. Record the walkthrough described in `presentation/walkthrough.md`, add the video or a public video link here.
5. Confirm the public repository contains source, report, results, diagrams, and presentation evidence before submitting its link.

## References

The measurement protocol and scoring requirements follow the supplied Qiskit Fall Fest 2026 Basic Track brief. API choices follow the official [Qiskit IBM Runtime fake-provider documentation](https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/fake-provider) and [Qiskit Aer noise-model documentation](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html).

