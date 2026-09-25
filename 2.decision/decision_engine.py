"""Multi-criteria decision model with value of information.

The model is three ideas:

  1. Score each alternative on weighted criteria (compensation, growth, ...).
  2. Rank alternatives by weighted total.
  3. Ask which unknown fact would most improve the decision if you learned it.

Uncertainty is explicit: for some criteria an alternative has a distribution of
possible scores (scenarios with probabilities), not a single number. Value of
information measures how much better you could choose *in expectation* if one
of those unknowns became known before you decide.

Run:  uv run python decision_engine.py
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Problem representation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Criterion:
    """One axis of comparison, with a weight in the final score."""

    name: str
    weight: float


@dataclass
class Alternative:
    """One option (e.g. a job offer). Scores are 0–10 unless noted."""

    name: str
    # Known scores: criterion name -> value on 0–10 scale.
    scores: dict[str, float] = field(default_factory=dict)
    # Uncertain scores: criterion name -> list of (probability, score).
    uncertain: dict[str, list[tuple[float, float]]] = field(default_factory=dict)


def normalize_weights(criteria: list[Criterion]) -> list[Criterion]:
    """Return criteria whose weights sum to 1."""
    total = sum(c.weight for c in criteria)
    if total <= 0:
        raise ValueError("criteria weights must sum to a positive number")
    return [Criterion(c.name, c.weight / total) for c in criteria]


def expected_score(alt: Alternative, criterion: str) -> float:
    """Point estimate for one cell: known value or probability-weighted mean."""
    if criterion in alt.scores:
        return alt.scores[criterion]
    scenarios = alt.uncertain.get(criterion)
    if not scenarios:
        raise KeyError(f"{alt.name} has no score for {criterion}")
    return sum(p * s for p, s in scenarios)


def weighted_total(alt: Alternative, criteria: list[Criterion]) -> float:
    """Weighted sum using expected scores (0–10 scale per criterion)."""
    return sum(c.weight * expected_score(alt, c.name) * 10 for c in criteria)


def rank(
    alternatives: list[Alternative],
    criteria: list[Criterion],
) -> list[tuple[Alternative, float]]:
    """Alternatives sorted best-first by weighted total."""
    criteria = normalize_weights(criteria)
    scored = [(alt, weighted_total(alt, criteria)) for alt in alternatives]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Value of information
# ---------------------------------------------------------------------------


def _resolve(
    alt: Alternative,
    criterion: str,
    scenario_index: int,
) -> Alternative:
    """Return a copy with one uncertain criterion fixed to a scenario."""
    scenarios = alt.uncertain[criterion]
    _, value = scenarios[scenario_index]
    scores = dict(alt.scores)
    scores[criterion] = value
    uncertain = {k: v for k, v in alt.uncertain.items() if k != criterion}
    return Alternative(name=alt.name, scores=scores, uncertain=uncertain)


def _first_open_uncertainty(
    alternatives: list[Alternative],
) -> tuple[int, str] | None:
    """Pick one unresolved uncertain cell (alt index, criterion name)."""
    for i, alt in enumerate(alternatives):
        for name in alt.uncertain:
            return i, name
    return None


def expected_optimal_value(
    alternatives: list[Alternative],
    criteria: list[Criterion],
) -> float:
    """Ex-ante expected score of the best alternative.

    Every uncertain criterion is integrated by enumerating scenarios. When no
    uncertainty remains, this is simply the top ranked score.
    """
    criteria = normalize_weights(criteria)
    slot = _first_open_uncertainty(alternatives)
    if slot is None:
        return rank(alternatives, criteria)[0][1]

    alt_index, crit = slot
    ev = 0.0
    for idx, (prob, _) in enumerate(alternatives[alt_index].uncertain[crit]):
        resolved = list(alternatives)
        resolved[alt_index] = _resolve(alternatives[alt_index], crit, idx)
        ev += prob * expected_optimal_value(resolved, criteria)
    return ev


def act_now_value(
    alternatives: list[Alternative],
    criteria: list[Criterion],
) -> float:
    """Score when you must commit today using only expected criterion scores."""
    return rank(alternatives, criteria)[0][1]


def value_of_information(
    alternatives: list[Alternative],
    criteria: list[Criterion],
) -> list[tuple[str, float]]:
    """Expected gain from learning each uncertain criterion perfectly.

    Compares «pick the best alternative on expected scores today» with «learn
    this one unknown, then pick the best alternative.» That matches the course
    notion of which question is worth asking before you decide.

    Returns (criterion_name, evpi) sorted largest first. EVPI is in the same
    units as weighted_total (0–100 scale when scores are 0–10).
    """
    criteria = normalize_weights(criteria)
    baseline = act_now_value(alternatives, criteria)

    uncertain_names: set[str] = set()
    for alt in alternatives:
        uncertain_names.update(alt.uncertain.keys())

    results = []
    for name in uncertain_names:
        # Learning `name`: the true scenario is revealed before you choose.
        holders = [i for i, a in enumerate(alternatives) if name in a.uncertain]
        if not holders:
            continue
        alt_index = holders[0]
        with_info = 0.0
        for idx, (prob, _) in enumerate(alternatives[alt_index].uncertain[name]):
            resolved = list(alternatives)
            resolved[alt_index] = _resolve(alternatives[alt_index], name, idx)
            with_info += prob * act_now_value(resolved, criteria)
        results.append((name, with_info - baseline))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def decision_confidence(rankings: list[tuple[Alternative, float]]) -> str:
    """Coarse label from gap between first and second place."""
    if len(rankings) < 2:
        return "LOW"
    gap = rankings[0][1] - rankings[1][1]
    if gap >= 8:
        return "LOW"
    if gap >= 3:
        return "MEDIUM"
    return "HIGH"


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

QUESTIONS_FOR_CRITERION = {
    "Technical depth": [
        "What would I own in the first 90 days — services, data, or platform?",
        "How much of the stack is greenfield vs. maintenance?",
        "Who are the two engineers I'd pair with most often?",
    ],
    "Work-life balance": [
        "How many people left the team in the last year?",
        "Is the manager new to the team?",
        "What's the budget outlook for this group?",
    ],
    "compensation": [
        "What is the equity refresh policy?",
        "How does bonus target depend on company vs. individual performance?",
        "Are there sign-on or retention components not in the offer letter?",
    ],
}


def career_value_rupees(score_points: float, lakhs_per_point: float = 0.15) -> float:
    """Map decision-score points to a career-value equivalent in ₹ lakhs/year."""
    return score_points * lakhs_per_point


def format_report(
    alternatives: list[Alternative],
    criteria: list[Criterion],
    *,
    lakhs_per_point: float = 0.15,
) -> str:
    """Human-readable summary including VoI and suggested questions."""
    criteria = normalize_weights(criteria)
    rankings = rank(alternatives, criteria)
    voi = value_of_information(alternatives, criteria)
    confidence = decision_confidence(rankings)

    lines = [
        "MULTI-CRITERIA RANKING (expected scores)",
        "----------------------------------------",
    ]
    for alt, score in rankings:
        lines.append(f"  {alt.name:<22} {score:5.1f} / 100")
    lines.append("")
    lines.append(f"Decision uncertainty: {confidence}")
    if len(rankings) >= 2:
        gap = rankings[0][1] - rankings[1][1]
        lines.append(
            f"  (leader {rankings[0][0].name} ahead of "
            f"{rankings[1][0].name} by {gap:.1f} points)"
        )
    lines.append("")
    lines.append("VALUE OF INFORMATION")
    lines.append("--------------------")
    if not voi:
        lines.append("  All criteria are known — nothing left to resolve.")
    else:
        for name, gain in voi:
            rupees = career_value_rupees(gain, lakhs_per_point)
            lines.append(
                f"  {name:<22} +{gain:4.1f} pts  "
                f"(~₹{rupees:.2f}L/yr career-value equivalent)"
            )
        top_name = voi[0][0]
        lines.append("")
        lines.append("RECOMMENDATION")
        lines.append("--------------")
        if voi[0][1] <= 0.01:
            lines.append(
                "  Expected scores already separate the leaders — "
                "VoI is low for every unknown."
            )
        else:
            lines.append(
                f"  Resolve «{top_name}» first — it has the highest expected value."
            )
        key = top_name.lower()
        questions = QUESTIONS_FOR_CRITERION.get(key)
        if questions:
            lines.append("  Ask the hiring manager:")
            for q in questions:
                lines.append(f"    • {q}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def figure_ranking(
    alternatives: list[Alternative],
    criteria: list[Criterion],
    out: str = "decision_ranking.png",
):
    """Bar chart of expected weighted scores."""
    criteria = normalize_weights(criteria)
    rankings = rank(alternatives, criteria)
    names = [a.name for a, _ in rankings]
    scores = [s for _, s in rankings]
    colors = ["#2d6a4f" if i == 0 else "#40916c" if i == 1 else "#95d5b2"
              for i in range(len(names))]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(names, scores, color=colors)
    ax.set_xlabel("Weighted score (0–100)")
    ax.set_title("Job choice — expected multi-criteria scores")
    ax.set_xlim(0, 100)
    for i, s in enumerate(scores):
        ax.text(s + 0.5, i, f"{s:.1f}", va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def figure_voi(
    alternatives: list[Alternative],
    criteria: list[Criterion],
    out: str = "decision_voi.png",
):
    """Bar chart of value-of-information by uncertain criterion."""
    voi = value_of_information(alternatives, criteria)
    if not voi:
        return None
    names = [n for n, _ in voi]
    gains = [g for _, g in voi]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(names, gains, color="#4361ee")
    ax.set_ylabel("Expected score gain (points)")
    ax.set_title("Value of perfect information\n(which unknown helps most?)")
    top = max(gains) if gains else 1.0
    ax.set_ylim(0, max(top * 1.25, 0.5))
    for i, g in enumerate(gains):
        ax.text(i, g + 0.05 * max(gains, default=1), f"+{g:.1f}", ha="center")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def figure_criteria_breakdown(
    alternatives: list[Alternative],
    criteria: list[Criterion],
    out: str = "decision_breakdown.png",
):
    """Stacked contribution of each criterion to the leading alternative."""
    criteria = normalize_weights(criteria)
    leader = rank(alternatives, criteria)[0][0]
    labels = [c.name for c in criteria]
    contrib = [c.weight * expected_score(leader, c.name) * 10 for c in criteria]

    fig, ax = plt.subplots(figsize=(8, 4))
    left = 0.0
    for label, val in zip(labels, contrib):
        ax.barh([leader.name], [val], left=left, label=label)
        left += val
    ax.set_xlim(0, 100)
    ax.set_xlabel("Points toward weighted total")
    ax.set_title(f"Where {leader.name}'s score comes from")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Example: which job?
# ---------------------------------------------------------------------------


def job_choice_problem() -> tuple[list[Alternative], list[Criterion]]:
    """The example from the Model Thinking project note.

    Unknown «actual engineering scope» is uncertain Technical depth on the
    startup offer. Unknown team stability is uncertain Work-life balance on
    the enterprise offer.
    """
    criteria = normalize_weights(
        [
            Criterion("Compensation", 0.30),
            Criterion("Career growth", 0.25),
            Criterion("Technical depth", 0.20),
            Criterion("Brand", 0.10),
            Criterion("Work-life balance", 0.10),
            Criterion("Location", 0.05),
        ]
    )
    alternatives = [
        Alternative(
            name="BigTech offer",
            scores={
                "Compensation": 8.5,
                "Career growth": 7.0,
                "Technical depth": 6.0,
                "Brand": 9.0,
                "Work-life balance": 5.5,
                "Location": 6.0,
            },
        ),
        Alternative(
            name="Startup offer",
            scores={
                "Compensation": 6.5,
                "Career growth": 9.0,
                "Brand": 4.0,
                "Work-life balance": 4.0,
                "Location": 8.0,
            },
            uncertain={
                "Technical depth": [
                    (0.35, 10.0),  # broad ownership, staff-track scope
                    (0.45, 7.0),  # solid but bounded squad
                    (0.20, 3.5),  # mostly glue work
                ],
            },
        ),
        Alternative(
            name="Enterprise offer",
            scores={
                "Compensation": 8.0,
                "Career growth": 6.5,
                "Technical depth": 7.0,
                "Brand": 7.0,
                "Location": 7.0,
            },
            uncertain={
                "Work-life balance": [
                    (0.30, 9.0),  # stable team, sane on-call
                    (0.50, 6.5),  # typical enterprise churn
                    (0.20, 3.0),  # reorg / attrition risk
                ],
            },
        ),
    ]
    return alternatives, criteria


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def demo():
    # Two alternatives, one unknown: learning it should help.
    criteria = normalize_weights([Criterion("pay", 0.5), Criterion("fun", 0.5)])
    alts = [
        Alternative(name="A", scores={"pay": 8.0, "fun": 5.0}),
        Alternative(
            name="B",
            scores={"pay": 6.0},
            uncertain={"fun": [(0.5, 9.0), (0.5, 3.0)]},
        ),
    ]
    # Expected: A = 65, B = 60 (fun averages to 6) → A wins on expectations
    assert abs(weighted_total(alts[0], criteria) - 65) < 0.01
    assert abs(weighted_total(alts[1], criteria) - 60) < 0.01
    voi = value_of_information(alts, criteria)
    assert voi[0][0] == "fun"
    assert voi[0][1] > 0

    # If fun is certainly 9, B wins (75 vs 65).
    alts_sure = [
        alts[0],
        Alternative(name="B", scores={"pay": 6.0, "fun": 9.0}),
    ]
    assert rank(alts_sure, criteria)[0][0].name == "B"

    print("self-check ok — scoring and VoI behave as described above")


if __name__ == "__main__":
    demo()

    alternatives, criteria = job_choice_problem()
    print()
    print(format_report(alternatives, criteria))

    for path in (
        figure_ranking(alternatives, criteria),
        figure_voi(alternatives, criteria),
        figure_criteria_breakdown(alternatives, criteria),
    ):
        if path:
            print("wrote", path)
