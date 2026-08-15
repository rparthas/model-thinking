"""Schelling's segregation model.

The whole model is four rules:

  1. A grid of cells. Each cell is empty, or holds an agent of type A or type B.
  2. An agent looks at its 8 surrounding cells and counts the agents there.
  3. It is HAPPY if the share of those neighbors matching its own type is at
     least `tolerance`. Otherwise it is UNHAPPY.
  4. Each round, every unhappy agent moves to a random empty cell.

Nobody in this model wants segregation. Nobody even prefers a majority of their
own type when tolerance is below 50%. Run it and watch what the grid does anyway.

Run:  uv run python segregation_simulator.py
"""

import random

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

# What a cell can hold. The numbers are just labels; 0/1/2 also happen to be
# convenient for matplotlib's colour map later on.
EMPTY = 0
A = 1
B = 2

# Empty cells are white, type A is blue, type B is red. Index into this by the
# cell value, which is why EMPTY/A/B are 0/1/2.
COLORS = ListedColormap(["white", "#3b6fd4", "#d43b3b"])


def show(ax, grid):
    """Draw a grid on a matplotlib axis using the shared colour scheme."""
    return ax.imshow(grid, cmap=COLORS, vmin=0, vmax=2)


# ---------------------------------------------------------------------------
# Rule 1: the grid
# ---------------------------------------------------------------------------

def make_grid(size=50, empty_share=0.1, seed=0):
    """Build a size x size grid, randomly filled.

    `empty_share` of cells are left empty; the rest are split evenly between
    type A and type B. This starting grid is thoroughly mixed — that is the
    point of comparison for everything that follows.
    """
    rng = random.Random(seed)
    grid = []
    for _ in range(size):
        row = []
        for _ in range(size):
            if rng.random() < empty_share:
                row.append(EMPTY)
            else:
                row.append(A if rng.random() < 0.5 else B)
        grid.append(row)
    return grid


# ---------------------------------------------------------------------------
# Rule 2: what an agent can see
# ---------------------------------------------------------------------------

def neighbors(grid, row, col):
    """Return the contents of the up-to-8 cells surrounding (row, col).

    Cells on an edge or corner simply have fewer neighbors — the grid does not
    wrap around. Empty neighboring cells are included in the list; the happiness
    rule filters them out, because an empty lot is neither friend nor stranger.
    """
    found = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue  # this is the agent itself, not a neighbor
            r, c = row + dr, col + dc
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                found.append(grid[r][c])
    return found


# ---------------------------------------------------------------------------
# Rule 3: happiness
# ---------------------------------------------------------------------------

def same_type_share(grid, row, col):
    """Fraction of this agent's occupied neighbors that share its type.

    Returns None when the agent has no occupied neighbors at all — there is no
    fraction to compute, and such an agent is treated as content by default.
    """
    me = grid[row][col]
    occupied = [n for n in neighbors(grid, row, col) if n != EMPTY]
    if not occupied:
        return None
    same = sum(1 for n in occupied if n == me)
    return same / len(occupied)


def is_unhappy(grid, row, col, tolerance):
    """An agent is unhappy when too few of its neighbors are like it."""
    if grid[row][col] == EMPTY:
        return False  # empty cells have no opinions
    share = same_type_share(grid, row, col)
    if share is None:
        return False  # an isolated agent has nothing to be unhappy about
    return share < tolerance


# ---------------------------------------------------------------------------
# Rule 4: unhappy agents move
# ---------------------------------------------------------------------------

def step(grid, tolerance, rng):
    """Run one round. Returns (new_grid, number_of_agents_that_moved).

    Note the two-phase structure: first find *everyone* who is unhappy, then
    move them. Deciding and moving in a single pass would let an agent's move
    change the neighborhood of an agent that has not been checked yet, which
    would make the outcome depend on the order cells happen to be scanned in.
    """
    unhappy = []
    empties = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == EMPTY:
                empties.append((r, c))
            elif is_unhappy(grid, r, c, tolerance):
                unhappy.append((r, c))

    # Copy so the caller's grid is left untouched — handy for animation frames.
    new = [row[:] for row in grid]

    # Shuffle both lists so nobody gets priority from their position on the grid.
    rng.shuffle(unhappy)
    rng.shuffle(empties)

    moved = 0
    # zip stops at the shorter list: if 300 agents are unhappy but only 250 empty
    # cells exist, 250 move this round and the rest try again next round.
    for (old_r, old_c), (new_r, new_c) in zip(unhappy, empties):
        new[new_r][new_c] = new[old_r][old_c]
        new[old_r][old_c] = EMPTY
        moved += 1
    return new, moved


# ---------------------------------------------------------------------------
# Measuring the outcome
# ---------------------------------------------------------------------------

def segregation(grid):
    """Average same-type-neighbor share across every agent on the grid.

    This is the one number that summarises the whole grid. A randomly mixed
    starting grid scores about 0.50: an average agent is surrounded by half its
    own type, half the other. A fully sorted grid approaches 1.00.

    Read it as: "the typical agent's neighborhood is X% people like them."
    """
    shares = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == EMPTY:
                continue
            share = same_type_share(grid, r, c)
            if share is not None:
                shares.append(share)
    return sum(shares) / len(shares)


def unhappy_count(grid, tolerance):
    return sum(is_unhappy(grid, r, c, tolerance)
               for r in range(len(grid))
               for c in range(len(grid[0])))


def run(grid, tolerance, max_rounds=100, seed=0):
    """Run rounds until nobody wants to move (or max_rounds is hit).

    Returns the list of grids, one per round, starting with the grid handed in.
    The simulation reaching a state where nobody moves is called an equilibrium:
    every agent is happy where it is, so the grid stops changing forever.
    """
    rng = random.Random(seed)
    history = [grid]
    for _ in range(max_rounds):
        grid, moved = step(grid, tolerance, rng)
        history.append(grid)
        if moved == 0:
            break
    return history


# ---------------------------------------------------------------------------
# Watching it happen
# ---------------------------------------------------------------------------

def trace(tolerance=0.4, size=50, max_rounds=100):
    """Print what happens round by round, so the numbers are not a black box."""
    grid = make_grid(size)
    print(f"\n--- tolerance {tolerance:.0%}: agent wants >= {tolerance:.0%} "
          f"of its neighbors to be its own type ---")
    print(f"round  unhappy agents  segregation")
    print(f"{0:>5}  {unhappy_count(grid, tolerance):>14}  "
          f"{segregation(grid):>10.0%}   <- random start")
    history = run(grid, tolerance, max_rounds)
    last = len(history) - 1
    for i, g in enumerate(history[1:], start=1):
        n = unhappy_count(g, tolerance)
        note = "   <- nobody wants to move: equilibrium" if n == 0 else ""
        if i <= 5 or i == last:
            print(f"{i:>5}  {n:>14}  {segregation(g):>10.0%}{note}")
        elif i == 6:
            print(f"{'...':>5}")
    return history


def animate(tolerance=0.4, size=50, out="schelling.gif"):
    """Save a GIF of the grid sorting itself out."""
    history = run(make_grid(size), tolerance)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")
    image = show(ax, history[0])
    title = ax.set_title("")

    def draw(i):
        image.set_data(history[i])
        title.set_text(f"tolerance {tolerance:.0%}   round {i}   "
                       f"segregation {segregation(history[i]):.0%}")
        return image, title

    anim = animation.FuncAnimation(fig, draw, frames=len(history), interval=200)
    anim.save(out, writer="pillow", fps=5)
    plt.close(fig)
    return out


def sweep(tolerances=(0.2, 0.3, 0.4, 0.5, 0.6), size=50,
          out="schelling_sweep.png"):
    """Run the same starting grid at several tolerances and compare endings.

    Top row: the final grid. Bottom row: segregation over time, on a shared
    y-axis so the curves are directly comparable. The dashed line marks 50%,
    where the random starting grid sits.
    """
    fig, axes = plt.subplots(2, len(tolerances),
                             figsize=(3.5 * len(tolerances), 7))
    finals = {}
    for i, t in enumerate(tolerances):
        history = run(make_grid(size), t)
        curve = [segregation(g) for g in history]
        finals[t] = curve[-1]

        show(axes[0, i], history[-1])
        axes[0, i].axis("off")
        axes[0, i].set_title(f"tolerance {t:.0%}\n"
                             f"segregation {curve[-1]:.0%} "
                             f"after {len(curve) - 1} rounds")

        axes[1, i].plot(curve)
        axes[1, i].axhline(0.5, linestyle="--", linewidth=1, color="grey")
        axes[1, i].set_ylim(0.4, 1.0)
        axes[1, i].set_xlabel("round")
        axes[1, i].set_ylabel("segregation" if i == 0 else "")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return finals


def figure_happiness_rule(out="schelling_rule.png"):
    """Draw three small neighborhoods and whether their centre agent is happy.

    Used by schelling_explained.md to show the happiness rule on cases small
    enough to count by hand.
    """
    cases = [
        [[A, A, B], [B, A, EMPTY], [A, EMPTY, B]],
        [[B, B, B], [B, A, EMPTY], [A, EMPTY, B]],
        [[B, B, EMPTY], [B, A, EMPTY], [EMPTY, EMPTY, EMPTY]],
    ]
    fig, axes = plt.subplots(1, len(cases), figsize=(3.4 * len(cases), 4.4))
    for ax, cells in zip(axes, cases):
        show(ax, cells)
        ax.set_xticks([])
        ax.set_yticks([])
        for r in range(3):
            for c in range(3):
                name = {EMPTY: "", A: "A", B: "B"}[cells[r][c]]
                bold = "bold" if (r, c) == (1, 1) else "normal"
                colour = "white" if cells[r][c] != EMPTY else "black"
                ax.text(c, r, name, ha="center", va="center", color=colour,
                        fontsize=16, fontweight=bold)
        # Outline the centre agent — the one whose happiness we are judging.
        ax.add_patch(plt.Rectangle((0.5, 0.5), 1, 1, fill=False,
                                   edgecolor="black", linewidth=3))
        # Count the same way the model does, so the caption cannot drift from
        # the rule: occupied neighbors only, empty cells ignored.
        occupied = [n for n in neighbors(cells, 1, 1) if n != EMPTY]
        same = sum(1 for n in occupied if n == cells[1][1])
        share = same_type_share(cells, 1, 1)
        verdict = "happy" if not is_unhappy(cells, 1, 1, 0.4) else "UNHAPPY"
        ax.set_title(f"{same} of {len(occupied)} neighbors match\n"
                     f"share = {share:.0%}\n"
                     f"at 40% tolerance: {verdict}", fontsize=11)
    fig.suptitle("The happiness rule, judged for the outlined centre agent "
                 "(white = empty)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def figure_before_after(tolerance=0.4, size=50, out="schelling_before_after.png"):
    """Start grid next to its equilibrium, for the same run."""
    history = run(make_grid(size), tolerance)
    fig, axes = plt.subplots(1, 2, figsize=(9, 5))
    for ax, g, label in ((axes[0], history[0], "round 0: random"),
                         (axes[1], history[-1],
                          f"round {len(history) - 1}: equilibrium")):
        show(ax, g)
        ax.axis("off")
        ax.set_title(f"{label}\nsegregation {segregation(g):.0%}")
    fig.suptitle(f"No agent wanted this. Each only asked that {tolerance:.0%} "
                 f"of its neighbors match.", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# A tiny hand-checkable example, so the rules above are verifiable by eye
# ---------------------------------------------------------------------------

def demo():
    grid = [[A, A, EMPTY],
            [A, B, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

    # The B in the middle touches 3 agents, all of them A. Its same-type share
    # is 0/3 = 0%, so it is unhappy at any tolerance above zero.
    assert same_type_share(grid, 1, 1) == 0.0
    assert is_unhappy(grid, 1, 1, 0.4)

    # The A at top-left touches 3 agents: two A and one B. Share = 2/3 = 67%.
    # Happy when it needs 40% of its own type, unhappy when it needs 70%.
    assert round(same_type_share(grid, 0, 0), 2) == 0.67
    assert not is_unhappy(grid, 0, 0, 0.4)
    assert is_unhappy(grid, 0, 0, 0.7)

    # Empty cells never count as unhappy, even at an impossible tolerance.
    assert not is_unhappy(grid, 2, 2, 1.0)

    # A grid already sorted into two blocks is highly segregated and stable:
    # every agent is happy, so nobody moves and it never changes again.
    sorted_grid = [[A] * 4, [A] * 4, [B] * 4, [B] * 4]
    assert segregation(sorted_grid) > 0.8
    assert unhappy_count(sorted_grid, 0.4) == 0

    print("self-check ok — the rules behave as described above")


if __name__ == "__main__":
    demo()

    # Watch one run unfold, then compare across tolerances.
    trace(tolerance=0.3)
    trace(tolerance=0.4)

    print("\n--- final segregation by tolerance ---")
    print("random starting grid is always ~50%\n")
    for t, s in sweep().items():
        bar = "#" * round(s * 40)
        print(f"tolerance {t:.0%}  segregation {s:>4.0%}  {bar}")

    for path in (animate(), figure_happiness_rule(), figure_before_after()):
        print("wrote", path)
