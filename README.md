# Model Thinking

Exercises from Scott E. Page's [Model Thinking](https://www.coursera.org/learn/model-thinking) course on Coursera. Each module of the course introduces a family of models; this repository holds a runnable implementation for each one, along with the experiments and visualizations that make the model's central insight visible.

Every model lives in its own self-contained Python script, written to be read rather than to be fast: plain loops over plain lists, one function per rule of the model, and comments that explain the modeling choices instead of restating the syntax. Each script runs standalone, verifies its own rules against a small hand-checkable example on start, prints its results, and writes its figures next to itself. Each model also gets a companion `*_explained.md` walkthrough.

Dependencies are managed with [uv](https://docs.astral.sh/uv/). `uv run` creates and syncs the environment on first use, so no separate install step is needed. Matplotlib is the only real dependency; the models themselves use nothing but the standard library.

## Modules

### Module 1 — Segregation and Peer Effects

Schelling's segregation model, in [`1.schelling-model/segregation_simulator.py`](1.schelling-model/segregation_simulator.py).

A grid holds two types of agents plus empty cells. An agent sees only its eight surrounding cells and is happy when at least `tolerance` of its occupied neighbors share its type. Each round, every unhappy agent relocates to a random empty cell. The simulation runs until nobody wants to move.

```bash
uv run python 1.schelling-model/segregation_simulator.py
```

That prints a round-by-round trace of one run and writes four figures:

| File | Shows |
|------|-------|
| `schelling_rule.png` | the happiness rule applied to neighborhoods small enough to count by hand |
| `schelling_before_after.png` | the random starting grid beside the equilibrium it settles into |
| `schelling.gif` | every round in between |
| `schelling_sweep.png` | final grids and segregation-over-time curves for all five tolerances |

![Before and after](1.schelling-model/schelling_before_after.png)

Segregation is measured as the mean share of same-type neighbors across all agents — read it as "the typical agent's neighborhood is X% people like them." A randomly mixed grid scores about 50%, and every run starts there.

| Tolerance | What the agent is asking for | Final segregation |
|-----------|------------------------------|-------------------|
| 20% | content outnumbered 4-to-1 | 57% |
| 30% | content outnumbered 7-to-3 | 76% |
| 40% | content outnumbered 3-to-2 | 83% |
| 50% | wants an even split | 87% |
| 60% | wants a modest majority | 97% |

The insight is the 30% row. Those agents are happy being a small minority — none of them wants a neighborhood of its own type, and none can even perceive the grid beyond its eight neighbors — yet they settle into a map where the typical neighborhood is three-quarters one type. Segregation here is nobody's preference; it is what the individual moves add up to. Macro patterns are not scaled-up micro preferences, which means you cannot read people's preferences off the outcome they collectively produce.

**[schelling_explained.md](1.schelling-model/schelling_explained.md) is the full walkthrough**: the rules in detail, why the code is structured the way it is, how to read the results, five experiments to try, and what the model deliberately leaves out.

### Module 2 — Aggregation and Decision Models

Multi-criteria decision engine with value of information, in [`2.decision/decision_engine.py`](2.decision/decision_engine.py).

Score alternatives on weighted criteria (compensation, growth, technical depth, …). Some cells stay uncertain as probability-weighted scenarios. The script ranks options on expected scores, then estimates **which unknown would most improve the decision** if you learned it before committing — with suggested questions to ask.

```bash
uv run python 2.decision/decision_engine.py
```

That runs a self-check, prints a job-choice report, and writes three figures:

| File | Shows |
|------|-------|
| `decision_ranking.png` | Expected weighted scores for each offer |
| `decision_voi.png` | Expected gain from perfect information per unknown |
| `decision_breakdown.png` | How the leading offer’s score splits across criteria |

The insight is not “compute a weighted sum.” It is that **acting on averages can hide flip points** — resolving the right unknown (here, startup technical scope) has measurable expected value even when the safe offer leads today.

**[decision_explained.md](2.decision/decision_explained.md)** covers the rules, the job example, how to reuse the API, and experiments to try.
