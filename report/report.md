# Project report

> **Status:** fill this report with one run using the organizer's common definitions before submission. The attached brief does not include those values. Do not present results from the starter profiles as official findings.

## Abstract

Question: How does processor connectivity affect preparation and verification of a Bell pair on two fixed ports, and does a ZZ parity check improve conditional fidelity enough to justify its cost?

**Results summary:** [Insert measured result, uncertainty, acceptance yield, and overhead from `results/comparison.md` after using official definitions.]

## 1. Problem and benchmark definitions

We prepare |Φ+> = (|00> + |11>)/√2 between the fixed output ports on three processor models: the 2016-inspired reference, the designated contemporary IBM-style backend snapshot, and the hyperbolic-inspired graph. List exact nodes, edges, ports, basis gates, noise values, shot count, and data source here. State whether these are exactly the organizer definitions.

## 2. Method

The logical preparation applies H to port 1 followed by CNOT to port 2. Transpilation constrains the circuit to the model coupling map and pins logical data qubits to the ports. Three Pauli parity circuits estimate XX, YY, and ZZ. Fidelity is `F = (1 + XX - YY + ZZ)/4`, with `σF = sqrt(σXX² + σYY² + σZZ²)/4`; each correlator's independent-shot uncertainty is `sqrt((1 - <PP>²)/N)`. A result counts as verified only if `F - 2σF > 0.5`.

Protection adds an ancilla initialized to |0>, computes the data ZZ parity, and post-selects ancilla outcome 0. Report conditional fidelity beside acceptance fraction and discarded shots. The check detects single X/Y errors and does not detect Z errors.

## 3. Results

Paste the generated nine-row comparison table from `results/comparison.md` here. Include the three coupling-map diagrams and identify ports and ancilla in every figure. Discuss any noise-model assumptions and the fact that a fake backend is a snapshot rather than a live hardware run.

| Processor | Case | F ± σF | Verified? | Depth | Two-qubit gates | SWAP overhead | Physical qubits | Yield | Discarded shots |
|---|---|---|---|---|---|---|---|---|---|
| 2016-inspired | Ideal | | | | | | | 1.000 | 0 |
| 2016-inspired | Noisy | | | | | | | | |
| 2016-inspired | Protected | | | | | | | | |
| Contemporary IBM-style | Ideal | | | | | | | 1.000 | 0 |
| Contemporary IBM-style | Noisy | | | | | | | | |
| Contemporary IBM-style | Protected | | | | | | | | |
| Hyperbolic-inspired | Ideal | | | | | | | 1.000 | 0 |
| Hyperbolic-inspired | Noisy | | | | | | | | |
| Hyperbolic-inspired | Protected | | | | | | | | |

## 4. Architecture comparison

For each architecture, relate fidelity changes to compiled depth, two-qubit operations, estimated routing overhead, and noise. Compare the protected case with its noisy baseline, including its fidelity gain (or loss), ancilla/gate cost, and accepted fraction. Distinguish connectivity effects from backend gate-set/noise differences. If using common noise and gates to isolate connectivity, report that as a separate controlled comparison.

## 5. Limitations

Discuss finite-shot uncertainty, the simplified circuit-level noise model (if used), routing and SWAP-estimate limitations, ancilla/check errors, and any differences between the simulated profile and actual device behavior. A finite graph comparison does not prove universal superiority of an architecture.

## 6. Recommendation

Recommend one specific hardware or software design choice for future quantum cloud systems. Tie it to measured comparisons and name the conditions where the recommendation may not hold.

## Reproducibility record

- Git commit: [fill]
- Python/Qiskit/Qiskit Aer versions: [fill]
- Config file and definition status: [fill]
- Seed and shots per setting: [fill]
- Run command: `bellbench run --config config/benchmark.yaml --output results --shots 4096`
- Raw counts and circuit summaries: `results/results.json`
