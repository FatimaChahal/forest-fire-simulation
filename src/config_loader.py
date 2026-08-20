"""config_loader.py — Lecture et validation du fichier de configuration."""

import json
from pathlib import Path

MAX_GRID_DIMENSION = 500  # limite raisonnable pour éviter blocages/lenteurs


class ConfigError(Exception):
    """Erreur levée quand la configuration est invalide."""


class ConfigLoader:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def load(self) -> dict:
        if not self.filepath.exists():
            raise ConfigError(f"Fichier de config introuvable : {self.filepath}")

        with open(self.filepath, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigError(f"JSON invalide : {e}")

        self._validate(config)
        return config

    def _validate(self, config: dict) -> None:
        h, l = config.get("hauteur"), config.get("largeur")

        if not isinstance(h, int) or h <= 0:
            raise ConfigError("hauteur invalide : doit être un entier positif")
        if h > MAX_GRID_DIMENSION:
            raise ConfigError(f"hauteur trop grande : max {MAX_GRID_DIMENSION}")

        if not isinstance(l, int) or l <= 0:
            raise ConfigError("largeur invalide : doit être un entier positif")
        if l > MAX_GRID_DIMENSION:
            raise ConfigError(f"largeur trop grande : max {MAX_GRID_DIMENSION}")

        p = config.get("probabilite_propagation")
        if not isinstance(p, (int, float)) or isinstance(p, bool) or not (0 <= p <= 1):
            raise ConfigError(
                "probabilite_propagation invalide : doit être entre 0 et 1"
            )

        positions = config.get("positions_feu_initial")
        if not positions:
            raise ConfigError("au moins une position de feu initial requise")

        for pos in positions:
            if not (isinstance(pos, list) and len(pos) == 2):
                raise ConfigError(f"position mal formée : {pos}")
            i, j = pos
            if not isinstance(i, int) or not isinstance(j, int):
                raise ConfigError(f"position {pos} : les coordonnées doivent être des entiers")
            if not (0 <= i < h and 0 <= j < l):
                raise ConfigError(f"position {pos} hors des limites de la grille")