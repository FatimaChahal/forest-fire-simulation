"""simulator.py — Logique de propagation du feu (règles du jeu)."""

import logging

import numpy as np

from src.grid import GRIS, ROUGE, VERT, Grid

logger = logging.getLogger(__name__)


class Simulator:
    """Applique les règles de propagation du feu sur une Grid."""

    def __init__(self, grid: Grid, p: float, seed: int | None = None) -> None:
        self.grid = grid
        self.p = p
        self.rng = np.random.default_rng(seed)

    def step(self) -> None:
        rouge_positions = list(zip(*np.where(self.grid.state == ROUGE)))

        for (i, j) in rouge_positions:
            self.grid.state[i, j] = GRIS

        new_fires = set()
        for (i, j) in rouge_positions:
            for (ni, nj) in self.grid.get_neighbors(i, j):
                if self.grid.state[ni, nj] == VERT and self.rng.random() < self.p:
                    new_fires.add((ni, nj))

        for (ni, nj) in new_fires:
            self.grid.state[ni, nj] = ROUGE

        logger.debug(
            f"step: {len(rouge_positions)} cases éteintes, "
            f"{len(new_fires)} nouvelles prises de feu"
        )

    def run(self, max_steps: int = 1000, keep_history: bool = True) -> list[np.ndarray]:
        """Fait tourner la simulation jusqu'à extinction.

        keep_history=False évite de stocker chaque étape en mémoire —
        utile pour de grandes grilles où seul le résultat final compte.
        """
        history = [self.grid.copy_state()] if keep_history else []
        steps = 0

        while self.grid.has_fire() and steps < max_steps:
            self.step()
            if keep_history:
                history.append(self.grid.copy_state())
            steps += 1
            logger.info(f"Étape {steps} terminée")

        if steps == max_steps:
            raise RuntimeError(
                "Simulation arrêtée après max_steps sans extinction — "
                "vérifier la logique de propagation."
            )

        logger.info(f"Simulation terminée en {steps} étapes")
        return history