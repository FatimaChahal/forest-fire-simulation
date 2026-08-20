"""grid.py — Représentation de l'état de la forêt (grille + états des cases)."""

from typing import ClassVar

import numpy as np

VERT, ROUGE, GRIS = 0, 1, 2


class Grid:
    """Représente l'état géométrique de la grille. Ne connaît AUCUNE règle
    de propagation (ça, c'est le rôle du Simulator) — Grid reste neutre.
    """

    def __init__(self, h: int, l: int) -> None:
        self.h = h
        self.l = l
        self.state = np.full((h, l), VERT, dtype=np.int8)

    def set_fire(self, positions: list[tuple[int, int]]) -> None:
        for (i, j) in positions:
            self.state[i, j] = ROUGE

    def get_neighbors(self, i: int, j: int) -> list[tuple[int, int]]:
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.h and 0 <= nj < self.l:
                neighbors.append((ni, nj))
        return neighbors

    def has_fire(self) -> bool:
        return bool(np.any(self.state == ROUGE))

    def copy_state(self) -> np.ndarray:
        return self.state.copy()

    def count(self, cell_type: int) -> int:
        """Compte le nombre de cases dans un état donné (utile pour les résumés)."""
        return int(np.sum(self.state == cell_type))


class GridRenderer:
    """Responsable UNIQUEMENT de l'affichage visuel d'une Grid."""

    SYMBOLS: ClassVar[dict[int, str]] = {VERT: "🟩", ROUGE: "🔴", GRIS: "⬜"}

    @staticmethod
    def render(grid: Grid) -> str:
        return "\n".join(
            "".join(GridRenderer.SYMBOLS[cell] for cell in row)
            for row in grid.state
        )