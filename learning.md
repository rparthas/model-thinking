
## Phase 1 — Learn to see emergence

### Module 1 — Segregation & Peer Effects

**Build:** `segregation_simulator.py`

Model a grid containing two types of agents.

Each agent has a tolerance:

```text
"If at least 40% of my neighbors are like me → I'm happy."
```

Run the simulation.

### Experiment

Change tolerance:

```text
20%
30%
40%
50%
60%
```

Measure:

```text
individual tolerance
        ↓
local decisions
        ↓
global segregation
```

### Visualization

Create an animation/grid showing the system evolving.

### Insight you're trying to discover

**Large-scale outcomes can emerge from individually mild preferences.**

This is exactly the kind of model Page introduces in Module 1. 

**Artifact:** one Python notebook + one visualization.

---

# Module 2 — Aggregation & Decision Models

### Build: `decision_engine.py`

This is the first project I'd make personally useful.

Create a generic multi-criteria decision model.

Example:

> Which job should I choose?

Inputs:

```text
Compensation       30%
Career growth      25%
Technical depth    20%
Brand              10%
Work-life balance  10%
Location             5%
```

Then calculate scores.

But add something more interesting:

### Value of Information

Ask:

> "Which unknown piece of information would most improve my decision?"

For example:

```text
Unknown: actual engineering scope

Current decision uncertainty: HIGH

Expected value of finding out:
₹X / career-value equivalent

Recommendation:
Ask hiring manager these 3 questions.
```

That's much more useful than simply learning decision trees.

The course explicitly covers multi-criteria decisions, probability, decision trees and **value of information** here. 

**Artifact:** reusable decision framework.

---

# Module 3 — Behavioral Models & Regression

### Build: `behavior_model.py`

Create three models of the **same phenomenon**:

```text
Rational model
Behavioral model
Rule-based model
```

Example:

> How does a person decide whether to switch jobs?

Then create synthetic data.

Fit:

```text
Linear regression
Categorical model
Non-linear model
```

Compare predictions.

### The important lesson

Don't ask:

> "Which model is correct?"

Ask:

> **"Under what conditions does each model become useful?"**

That's one of the most important ideas in the entire course.

Module 3 explicitly contrasts rational, behavioral and rule-based models before moving into categorical and linear models. 

**Artifact:** notebook comparing models.

---

# Module 4 — Tipping Points & Growth

This one is worth making slightly bigger.

### Build: `contagion_simulator.py`

Simulate:

```text
Population
    ↓
Contact network
    ↓
Probability of transmission
    ↓
Recovery
    ↓
New infections
```

Then experiment with:

```text
R₀
network density
initial infected %
recovery rate
```

But don't restrict yourself to disease.

Use the exact same model for:

```text
Disease
Product adoption
Technology adoption
Rumors
Ideas
AI adoption
```

That's the beautiful part.

### Then add growth

Compare:

```text
Linear growth
Exponential growth
Solow-style growth
```

Plot them together.

**Artifact:** contagion + growth simulator.

This module covers percolation, diffusion, SIS contagion and several growth models. 

---

# Module 5 — Diversity, Innovation & Markov Processes

This is where it gets interesting for you as an engineer.

### Build: `innovation_simulator.py`

Imagine a problem with a landscape:

```text
          /\        /\
     /\  /  \  /\  /  \
____/  \/    \/  \/    \____
```

Each point represents a possible solution.

An agent searches for better solutions.

Compare:

```text
Team A
Everyone uses same heuristic

vs.

Team B
Different heuristics

vs.

Team C
Random exploration + exploitation
```

Measure:

```text
best solution
time to best solution
variance
probability of getting stuck
```

Then add a **Markov model**.

Now you have:

```text
State A → State B → State C
   ↑         ↓
   └─────────┘
```

This becomes a generic state-transition engine.

**Artifact:** optimization + Markov simulator.

---

# Module 6 — Midterm

### Don't build anything.

Instead, create a single document:

## "My Model Thinking Toolkit"

For each model:

```text
Model
------
What problem does it solve?

Assumptions

Mechanism

What does it predict?

When does it fail?

What other model could explain the same thing?
```

This is important.

You're converting **knowledge → retrieval system**.

---

# Module 7 — Lyapunov Functions & Coordination

Don't over-engineer this one.

### Build: `convergence_lab.py`

Create systems where agents repeatedly interact.

Track a system-level function:

```text
V(t)
```

and observe:

```text
V(t+1) < V(t)
```

Plot:

```text
V
│\
│ \
│  \
│   \____
│        \____
└────────────── t
```

Then build a coordination game.

Example:

```text
Everyone uses Python
Everyone uses Java
```

Individually:

> "I'll use whatever everyone else uses."

Run the system from different starting conditions.

### Question

Why do some systems converge to an equilibrium while others don't?

That is the useful intuition.

Module 7 specifically uses Lyapunov functions to reason about equilibrium and convergence, alongside coordination and culture models. 

**Artifact:** convergence visualizer.

---

# Module 8 — Path Dependence & Networks

This one deserves a **serious mini-project**.

### Build: `network_lab.py`

Start with a simple Polya urn:

```text
Red   █████
Blue  ██
```

Every time you pick a color, you add another ball of that color.

Run it 10,000 times.

You'll see something fascinating:

**Tiny early randomness can produce huge long-term differences.**

Then build networks.

Compare:

```text
Random network

Small-world network

Scale-free network

Dense network
```

Measure:

```text
average path length
clustering
centrality
diffusion speed
```

### This becomes useful for:

- knowledge propagation
- organizational communication
- social networks
- data lineage
- dependency graphs
- technology adoption

Given your data-engineering background, I'd actually keep this project around permanently.

**Artifact:** reusable network-analysis/simulation library.

---

# Module 9 — Randomness & Random Walks

### Build: `luck_vs_skill.py`

This is one of the projects I'd strongly recommend.

Create agents with different skill levels:

```text
Skill = 0.55
Skill = 0.60
Skill = 0.70
Skill = 0.80
```

Add randomness.

Run:

```text
10 rounds
100 rounds
1,000 rounds
10,000 rounds
```

Then rank the agents.

You will see something counterintuitive:

**Short-term rankings can be dominated by luck even when underlying skill differs.**

Then build a random walk:

```text
price[t+1] = price[t] + random_shock
```

Compare observed patterns against a random process.

This connects beautifully with the course's treatment of skill vs. luck and random walks. 

**Artifact:** skill/luck simulator.

---

# Module 10 — Prisoner's Dilemma & Mechanism Design

### Build: `cooperation_lab.py`

Start with:

```text
             B Cooperates   B Defects

A Cooperates      3,3          0,5

A Defects         5,0          1,1
```

Then create repeated games.

Strategies:

```text
Always Cooperate
Always Defect
Tit-for-Tat
Grudger
Random
Forgiving Tit-for-Tat
```

Run tournaments.

Then change:

```text
payoffs
number of rounds
noise
population composition
```

Now ask:

> Under what conditions does cooperation emerge?

This is far more memorable than reading about the Prisoner's Dilemma.

The module also extends into collective action and mechanism design, including hidden information/action and auctions. 

**Artifact:** game-theory tournament engine.

---

# Module 11 — Replicator Dynamics & Prediction

### Build: `strategy_evolution.py`

Suppose a population has:

```text
Strategy A
Strategy B
Strategy C
```

Each produces different payoffs.

Every generation:

```text
successful strategies
        ↓
increase representation

unsuccessful strategies
        ↓
decrease representation
```

Plot:

```text
Population %
100│A
   │ A
 50│  A────
   │       B────
   │            B
  0└─────────────────
       generations
```

Then introduce mutation/randomness.

Now you've built a primitive **evolutionary strategy simulator**.

Module 11 culminates in replicator dynamics, prediction, variation and the "many model thinker." 

**Artifact:** evolutionary strategy simulator.

---

# Module 12 — Final Project

And **this is where I want you to break your "learning without doing" pattern.**

Don't take the final exam and call it done.

Build:

# Model Thinking Engine v1

It should accept:

```text
Problem
Assumptions
Variables
Possible interventions
```

Then allow you to select models:

```text
[✓] Decision Tree
[✓] Markov
[✓] Network
[✓] Contagion
[✓] Random Walk
[✓] Game Theory
[✓] Growth
```

Run simulations.

Return:

```text
MODEL 1
-------
Prediction:
...

MODEL 2
-------
Prediction:
...

MODEL 3
-------
Prediction:
...

ROBUST CONCLUSIONS
------------------
Things multiple models agree on:
...

MODEL-SPECIFIC CONCLUSIONS
--------------------------
...

KEY UNCERTAINTIES
-----------------
...
```

That is your **portfolio project**.

---

# Your 45-minute weekday schedule

Here's the important part.

Don't allocate 45 minutes to "studying."

Allocate it like this:

| Time | Activity |
|---|---|
| **20 min** | Course |
| **20 min** | Build |
| **5 min** | Write what you discovered |

That's it.

### Monday

**Learn**

Watch/read the model.

### Tuesday

**Implement**

Translate the model into Python.

### Wednesday

**Experiment**

Change parameters.

### Thursday

**Visualize**

Plot the results.

### Friday

**Explain**

Write:

```text
Model:
Assumptions:
Experiment:
Result:
Surprising observation:
Real-world implication:
```

### Weekend

You have 4–6 hours.

**Do NOT start another course.**

Use the weekend to:

- clean the code
- combine models
- build visualizations
- write documentation
- apply the model to a real problem

---

# Your project repository

I'd structure it like this:

```text
model-thinking-lab/
│
├── README.md
│
├── 01_segregation/
│   ├── model.py
│   ├── experiment.ipynb
│   └── README.md
│
├── 02_decision/
│
├── 03_behavior/
│
├── 04_contagion/
│
├── 05_innovation/
│
├── 06_model_toolkit/
│
├── 07_convergence/
│
├── 08_networks/
│
├── 09_randomness/
│
├── 10_games/
│
├── 11_evolution/
│
└── 12_model_engine/
```

And your README should eventually contain something like:

```text
I built 11 computational models while taking
Scott Page's Model Thinking course.

The goal was not to reproduce the lectures.

The goal was to turn abstract models into
executable systems and discover their behavior
through experimentation.
```

**That is a much stronger portfolio signal than "Completed Model Thinking — Coursera."**

---

# One important modification I'd make for YOU

You have a tendency to learn something and immediately find the **next interesting thing**.

So I would introduce a brutal constraint:

> **No new learning resource until the current artifact exists.**

For example:

```text
❌ Watch Module 1
❌ Read article about complexity
❌ Watch YouTube video about emergence
❌ Start another course

Instead:

✅ Watch Module 1
✅ Code Schelling
✅ Run 5 experiments
✅ Make one chart
✅ Write 5 observations
→ THEN continue
```

This is the behavioral change I think will matter most for you.

---

# And here's the bigger opportunity

There's a very nice intersection forming between the things you're already interested in:

```text
                 AI Engineering
                       │
                       │
                       ▼
             ┌──────────────────┐
             │  Model Thinking  │
             └────────┬─────────┘
                      │
             ┌────────┴─────────┐
             ▼                  ▼
       Data Engineering    Complex Systems
             │                  │
             └────────┬─────────┘
                      ▼
               AI / Agent Systems
```

Model thinking gives you a vocabulary for things that become **very important in AI systems**:

- agents
- emergence
- feedback loops
- network effects
- coordination
- incentives
- exploration/exploitation
- path dependence
- stochasticity
- adaptation
- equilibrium
- multi-agent interaction

So I wouldn't view this course as a random "thinking skills" course.

I'd use it as a **foundation for the kind of systems thinking that will make your AI engineering work stronger**.

And crucially, you'll learn it by **building**, not by collecting another 24 hours of lectures. The official course itself is roughly 24 hours and explicitly positions the models as tools for forecasting, decision-making, strategy and institutional design. 

### Your target outcome

Don't aim for:

> **"I completed Model Thinking."**

Aim for:

> **"I have a GitHub repo containing 10–12 computational models, and I can use several of them to reason about a new problem."**

That is the point where **learning has finally translated into action**.
