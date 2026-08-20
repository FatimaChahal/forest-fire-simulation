"""generate_gif.py — Génère un GIF animé de la propagation, pour le README.

Ce script est un outil de documentation, pas une IHM de simulation
(l'énoncé exclut explicitement l'IHM du périmètre évalué).
"""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from src.grid import GRIS, VERT, Grid
from src.simulator import Simulator

# Couleurs cohérentes avec l'affichage console (vert/rouge/gris)
CMAP = mcolors.ListedColormap(["#4CAF50", "#F44336", "#9E9E9E"])


def generate_gif(
    h: int = 20,
    l: int = 20,
    fire_start: tuple[int, int] = (10, 10),
    p: float = 0.55,
    seed: int = 7,
    output_path: str = "assets/propagation.gif",
) -> None:
    grid = Grid(h=h, l=l)
    grid.set_fire([fire_start])
    simulator = Simulator(grid, p=p, seed=seed)

    history = simulator.run(keep_history=True)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")
    im = ax.imshow(history[0], cmap=CMAP, vmin=VERT, vmax=GRIS)
    title = ax.set_title("Étape 0")

    def update(frame: int):
        im.set_data(history[frame])
        title.set_text(f"Étape {frame}")
        return im, title

    anim = FuncAnimation(fig, update, frames=len(history), interval=200)
    anim.save(output_path, writer=PillowWriter(fps=5))
    print(f"GIF généré : {output_path} ({len(history)} étapes)")


if __name__ == "__main__":
    generate_gif()