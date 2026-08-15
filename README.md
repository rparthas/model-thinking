# Model Thinking

Exercises from Scott E. Page's [Model Thinking](https://www.coursera.org/learn/model-thinking) course on Coursera. Each module of the course introduces a family of models; this repository holds a runnable implementation for each one, along with the experiments and visualizations that make the model's central insight visible.

Every model lives in its own self-contained Python script. Scripts run standalone, print a short self-check on start, and write their figures next to themselves.

Dependencies are managed with [uv](https://docs.astral.sh/uv/). `uv run` creates and syncs the environment on first use, so no separate install step is needed.

## Modules

### Module 1 — Segregation and Peer Effects

`segregation_simulator.py` implements Schelling's segregation model. A grid holds two types of agents plus empty cells. An agent is happy when at least `tolerance` of its occupied neighbors share its type; unhappy agents relocate to a random empty cell. The simulation runs until nobody wants to move.

Run it:

```bash
uv run python segregation_simulator.py
```

Outputs:

- `schelling.gif` — the grid evolving at 40% tolerance
- `schelling_sweep.png` — final grids and segregation-over-time curves for tolerances of 20%, 30%, 40%, 50%, and 60%

Segregation is measured as the mean share of same-type neighbors across all occupied cells. A randomly seeded grid starts near 50%.

| Tolerance | Final segregation |
|-----------|-------------------|
| 20%       | 57%               |
| 30%       | 75%               |
| 40%       | 84%               |
| 50%       | 87%               |
| 60%       | 98%               |

The insight: at 30% tolerance, every agent is content to be outnumbered two to one, and the grid still sorts itself to 75% segregation. Large-scale outcomes emerge from individually mild preferences — no agent in the model prefers a segregated neighborhood, yet segregation is what the system produces.
