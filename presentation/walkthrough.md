# Recorded walkthrough plan (5–7 minutes)

Record a screen-and-voice walkthrough and place the MP4 in this folder, or replace the video placeholder in the README with a stable public link. The repository does not contain a recording yet.

## Run of show

1. **0:00–0:35 — Question.** Explain why a Bell pair is a stronger target than Z-basis correlation alone.
2. **0:35–1:20 — Three geometries.** Show the three coupling-map figures. Highlight the fixed ports and point out which paths force routing.
3. **1:20–2:15 — Workflow.** Show the H + CNOT preparation, fixed initial layout, and the transpiled circuit summaries. Explain that routing and extra two-qubit gates are the geometry cost.
4. **2:15–3:05 — Verification.** Explain the XX, YY, ZZ measurements and the fidelity/uncertainty formula. Show why a classical 00/11 mixture has F=0.5 and the 95% rule.
5. **3:05–4:10 — Protection.** Show the ZZ parity ancilla circuit. State which errors it detects, which it misses, and explain that the fidelity is conditional on passing the check.
6. **4:10–5:30 — Results.** Walk through all nine cases in `results/comparison.md`: fidelity, uncertainty, depth, two-qubit gates, routing, qubits, yield, discarded shots.
7. **5:30–6:30 — Recommendation and limits.** Make one design recommendation supported by the measured table. Note finite graph, finite shots, modeled noise, and snapshot limits.

## Before recording

- Replace starter profiles with official definitions.
- Run the full configuration at the agreed shot count.
- Ensure all three diagrams and all nine rows are visible and readable.
- Use the actual measured results; do not narrate placeholder claims.
- Keep the clip under the organizer's time/file-size limit and check public-link access.
