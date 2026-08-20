"""main.py — Point d'entrée : charge la config, lance la simulation, affiche le résultat.

Usage:
    python3 main.py [config_path] [--detailed]
"""

import argparse
import logging
import sys

from src.config_loader import ConfigError, ConfigLoader
from src.grid import GRIS, VERT, Grid, GridRenderer
from src.simulator import Simulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main(config_path: str = "config.json", detailed: bool = False) -> None:
    """Charge la configuration, exécute la simulation, affiche le résultat.

    Args:
        config_path: chemin vers le fichier de config JSON.
        detailed: si True, affiche chaque étape ; sinon, affiche un résumé.
    """
    try:
        config = ConfigLoader(config_path).load()
    except ConfigError as e:
        logger.error(f"Configuration invalide : {e}")
        sys.exit(1)

    logger.info(f"Configuration chargée : {config}")

    grid = Grid(h=config["hauteur"], l=config["largeur"])
    positions = [tuple(pos) for pos in config["positions_feu_initial"]]
    grid.set_fire(positions)

    simulator = Simulator(
        grid,
        p=config["probabilite_propagation"],
        seed=config.get("seed"),
    )

    logger.info("Démarrage de la simulation...")
    history = simulator.run(keep_history=detailed)

    if detailed:
        for step_num, state in enumerate(history):
            print(f"\n--- Étape {step_num} ---")
            grid.restore_state(state)
            print(GridRenderer.render(grid))
    else:
        total_cells = grid.h * grid.l
        burned = grid.count(GRIS)
        intact = grid.count(VERT)
        print("\n--- Résumé de la simulation ---")
        print(f"Grille : {grid.h}x{grid.l} ({total_cells} cases)")
        print(f"Cases brûlées (cendres) : {burned} ({100 * burned / total_cells:.1f}%)")
        print(f"Cases intactes : {intact} ({100 * intact / total_cells:.1f}%)")
        print("\nÉtat final :")
        print(GridRenderer.render(grid))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulation de propagation d'un feu de forêt."
    )
    parser.add_argument(
        "config_path",
        nargs="?",
        default="config.json",
        help="Chemin vers le fichier de configuration JSON (défaut: config.json)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Affiche chaque étape de la simulation plutôt qu'un résumé",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Niveau de verbosité des logs (défaut: INFO)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.getLogger().setLevel(args.log_level)
    main(args.config_path, detailed=args.detailed)