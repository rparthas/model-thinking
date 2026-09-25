# Multi-Criteria Decisions and Value of Information, Explained

A walkthrough of the decision model in [`decision_engine.py`](decision_engine.py). The goal is not a spreadsheet that ranks options — it is a reusable framework that tells you **which unknown fact is worth resolving** before you commit.

---

## 1. The question the model answers

You have several options (job offers, vendors, cities) and several things you care about (pay, growth, balance). You can score each option on each dimension and apply weights. That part is familiar.

The harder question from Model Thinking Module 2 is:

> Given that some scores are guesses, **what should I try to learn next?**

Value of information (VoI) answers that. It compares:

1. **Act now** — pick the alternative with the highest *expected* weighted score.
2. **Learn, then act** — resolve one uncertain factor (e.g. real engineering scope), then pick the best alternative using what you know.

The gap is how many points (and, if you like, rupees of career value) that one conversation is worth in expectation.

---

## 2. The rules, in full

1. **Criteria and weights.** Each criterion has a weight; weights are normalized to sum to 1. Scores are on a 0–10 scale per criterion; the weighted total runs from 0–100.
2. **Known vs uncertain cells.** If you know a score, it is a single number. If not, you list scenarios `(probability, score)` for that alternative on that criterion.
3. **Ranking today.** `rank()` sorts alternatives by expected weighted total using probability-weighted means for uncertain cells.
4. **Value of information.** For each uncertain criterion, simulate resolving it (fix one scenario at a time, weighted by probability), re-rank, and measure the expected improvement over acting today.

Independence assumption: uncertain criteria on different offers are resolved separately; when one scenario is fixed, any remaining uncertainty still uses expected scores.

---

## 3. Worked example: three job offers

Weights match the project note:

| Criterion | Weight |
|-----------|--------|
| Compensation | 30% |
| Career growth | 25% |
| Technical depth | 20% |
| Brand | 10% |
| Work-life balance | 10% |
| Location | 5% |

**BigTech** is mostly known — strong pay and brand, moderate depth and balance.

**Startup** is attractive on growth and location, but **technical depth is uncertain** (that is the stand-in for “actual engineering scope” in the note).

**Enterprise** is solid on pay and depth, but **work-life balance is uncertain** (stand-in for team stability / reorg risk).

On expected scores alone, BigTech leads — but the margin over Enterprise is thin (**high decision uncertainty**). VoI is highest for **Technical depth** on the startup path: if scope is genuinely staff-level, the startup can overtake the safe choice; if it is glue work, BigTech looks even better.

Run the script for the current numbers and suggested hiring-manager questions:

```bash
cd 2.decision
uv run python decision_engine.py
```

Figures written next to the script:

| File | Shows |
|------|-------|
| `decision_ranking.png` | Expected weighted scores, best first |
| `decision_voi.png` | Expected point gain from perfect information per unknown |
| `decision_breakdown.png` | How the leader’s score splits across criteria |

---

## 4. How to reuse the framework

1. Copy `job_choice_problem()` or build a fresh list of `Alternative` and `Criterion` objects.
2. Put **only genuine unknowns** in `uncertain` — if you already blended a guess into a score, VoI will read as zero.
3. Call `format_report(alternatives, criteria)` for text output; adjust `lakhs_per_point` in `career_value_rupees()` to match how you translate points into money.
4. Extend `QUESTIONS_FOR_CRITERION` with the three questions you would actually ask for each unknown.

Core API:

```python
from decision_engine import (
    Alternative, Criterion, normalize_weights,
    rank, value_of_information, format_report,
)

criteria = normalize_weights([Criterion("pay", 0.6), Criterion("learning", 0.4)])
alts = [...]
print(format_report(alts, criteria))
```

---

## 5. Experiments to try

1. **Swing the weights.** Raise “Career growth” to 40% and re-run — does VoI shift from scope to stability?
2. **Add a fourth offer** with different uncertainty structure; watch VoI reorder.
3. **Collapse uncertainty.** Replace a scenario list with a single known score; confirm VoI for that criterion drops to ~0.
4. **Stress-test the act-now rule.** Build a tiny two-alternative problem like the self-check in `demo()` where the leader on expectations is *not* the one you would pick if you knew the truth — VoI should spike.

---

## 6. What this model deliberately leaves out

- **Correlated unknowns** (scope and funding runway moving together).
- **Cost of information** (recruiter time, offer expiry) — VoI here is gross value, not net of interview effort.
- **Continuous distributions** — scenarios are discrete; for a first tool that keeps the math visible, that is intentional.

Those are extensions, not flaws. The artifact you want from Module 2 is a **reusable decision framework** you can point at the next real choice — not a one-off spreadsheet.
