"""Schelling segregation model.

Grid of two agent types plus empty cells. An agent is happy when at least
`tolerance` of its occupied neighbors share its type; unhappy agents move to a
random empty cell. Run this file to produce an animation and a tolerance sweep.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.signal import convolve2d

EMPTY, A, B = 0, 1, 2
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def make_grid(n=50, empty_frac=0.1, seed=0):
    rng = np.random.default_rng(seed)
    cells = rng.choice([EMPTY, A, B], size=n * n, p=[empty_frac,
                                                     (1 - empty_frac) / 2,
                                                     (1 - empty_frac) / 2])
    return cells.reshape(n, n)


def _neighbor_counts(grid):
    a = convolve2d((grid == A).astype(int), KERNEL, mode="same")
    b = convolve2d((grid == B).astype(int), KERNEL, mode="same")
    return a, b


def unhappy_mask(grid, tolerance):
    a, b = _neighbor_counts(grid)
    total = a + b
    same = np.where(grid == A, a, b)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.divide(same, total, out=np.ones_like(same, float), where=total > 0)
    return (grid != EMPTY) & (frac < tolerance)


def segregation(grid):
    """Mean share of same-type neighbors across occupied cells."""
    a, b = _neighbor_counts(grid)
    total = a + b
    same = np.where(grid == A, a, b)
    occupied = (grid != EMPTY) & (total > 0)
    return float((same[occupied] / total[occupied]).mean())


def step(grid, tolerance, rng):
    """One round: every unhappy agent moves to a random empty cell."""
    grid = grid.copy()
    movers = np.argwhere(unhappy_mask(grid, tolerance))
    empties = np.argwhere(grid == EMPTY)
    if len(movers) == 0 or len(empties) == 0:
        return grid, 0
    rng.shuffle(movers)
    rng.shuffle(empties)
    for (r, c), (er, ec) in zip(movers, empties):
        grid[er, ec], grid[r, c] = grid[r, c], EMPTY
    return grid, min(len(movers), len(empties))


def run(grid, tolerance, rounds=100, seed=0):
    """Yield (grid, moves) per round, stopping early once nobody moves."""
    rng = np.random.default_rng(seed)
    for _ in range(rounds):
        grid, moves = step(grid, tolerance, rng)
        yield grid, moves
        if moves == 0:
            return


def animate(tolerance=0.4, n=50, rounds=100, out="schelling.gif"):
    frames = [make_grid(n)]
    frames += [g for g, _ in run(frames[0], tolerance, rounds)]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")
    im = ax.imshow(frames[0], cmap="coolwarm", vmin=0, vmax=2)
    title = ax.set_title("")

    def draw(i):
        im.set_data(frames[i])
        title.set_text(f"tolerance {tolerance:.0%}  round {i}  "
                       f"segregation {segregation(frames[i]):.0%}")
        return im, title

    anim = animation.FuncAnimation(fig, draw, frames=len(frames), interval=200)
    anim.save(out, writer="pillow", fps=5)
    plt.close(fig)
    return out


def sweep(tolerances=(0.2, 0.3, 0.4, 0.5, 0.6), n=50, rounds=100,
          out="schelling_sweep.png"):
    fig, axes = plt.subplots(2, len(tolerances), figsize=(4 * len(tolerances), 8))
    results = {}
    for i, t in enumerate(tolerances):
        start = make_grid(n)
        history = [segregation(start)]
        grid = start
        for grid, _ in run(start, t, rounds):
            history.append(segregation(grid))
        results[t] = history[-1]
        axes[0, i].imshow(grid, cmap="coolwarm", vmin=0, vmax=2)
        axes[0, i].axis("off")
        axes[0, i].set_title(f"tolerance {t:.0%}\nsegregation {history[-1]:.0%}")
        axes[1, i].plot(history)
        axes[1, i].set_ylim(0.4, 1.0)
        axes[1, i].set_xlabel("round")
        axes[1, i].set_ylabel("segregation" if i == 0 else "")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return results


def demo():
    grid = np.array([[A, A, EMPTY],
                     [A, B, EMPTY],
                     [EMPTY, EMPTY, EMPTY]])
    # centre B has 3 A-neighbours and 0 B-neighbours -> unhappy at any tolerance > 0
    assert unhappy_mask(grid, 0.4)[1, 1]
    # corner A has 2 A-neighbours out of 3 -> happy at 40%, unhappy at 60%
    assert not unhappy_mask(grid, 0.4)[0, 0]
    assert unhappy_mask(grid, 0.7)[0, 0]
    # empty cells are never unhappy
    assert not unhappy_mask(grid, 1.0)[grid == EMPTY].any()
    # a fully sorted grid is maximally segregated and stable
    sorted_grid = np.array([[A] * 4, [A] * 4, [B] * 4, [B] * 4])
    assert segregation(sorted_grid) > 0.8
    assert unhappy_mask(sorted_grid, 0.4).sum() == 0
    print("self-check ok")


if __name__ == "__main__":
    demo()
    print("animation:", animate())
    for t, s in sweep().items():
        print(f"tolerance {t:.0%} -> segregation {s:.0%}")
