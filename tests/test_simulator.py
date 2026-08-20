"""tests/test_simulator.py — Tests unitaires couvrant les cas extrêmes."""

import pytest

from src.config_loader import ConfigError, ConfigLoader
from src.grid import GRIS, ROUGE, VERT, Grid
from src.simulator import Simulator


class TestSimulatorEdgeCases:

    def test_p_zero_no_propagation(self):
        """Avec p=0, le feu s'éteint sans jamais se propager."""
        grid = Grid(h=5, l=5)
        grid.set_fire([(2, 2)])
        sim = Simulator(grid, p=0.0, seed=1)

        history = sim.run()

        # 2 étapes seulement : état initial + une étape où le feu s'éteint
        assert len(history) == 2
        assert not grid.has_fire()
        # La case initiale doit être grise, pas rouge
        assert grid.state[2, 2] == GRIS

    def test_p_one_full_propagation(self):
        """Avec p=1, toute la grille connexe finit par brûler."""
        grid = Grid(h=3, l=3)
        grid.set_fire([(1, 1)])  # centre
        sim = Simulator(grid, p=1.0, seed=1)

        sim.run()

        # Aucune case ne doit rester verte
        assert not (grid.state == VERT).any()

    def test_fire_in_corner_has_two_neighbors(self):
        """Une case en coin ne doit avoir que 2 voisins valides."""
        grid = Grid(h=5, l=5)
        neighbors = grid.get_neighbors(0, 0)
        assert len(neighbors) == 2
        assert (1, 0) in neighbors
        assert (0, 1) in neighbors

    def test_single_cell_grid(self):
        """Grille 1x1 : la simulation doit se terminer immédiatement."""
        grid = Grid(h=1, l=1)
        grid.set_fire([(0, 0)])
        sim = Simulator(grid, p=1.0, seed=1)

        history = sim.run()

        assert len(history) == 2
        assert grid.state[0, 0] == GRIS

    def test_multiple_initial_fires(self):
        """Plusieurs feux initiaux doivent tous être pris en compte."""
        grid = Grid(h=5, l=5)
        grid.set_fire([(0, 0), (4, 4)])

        assert grid.state[0, 0] == ROUGE
        assert grid.state[4, 4] == ROUGE
        assert grid.has_fire()


class TestConfigValidation:

    def test_probability_out_of_range_raises(self, tmp_path):
        """Une probabilité hors [0,1] doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": 5, '
            '"positions_feu_initial": [[2,2]], '
            '"probabilite_propagation": 1.5}'
        )

        with pytest.raises(ConfigError, match="probabilite_propagation"):
            ConfigLoader(str(config_file)).load()

    def test_position_out_of_grid_raises(self, tmp_path):
        """Une position de feu hors grille doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": 5, '
            '"positions_feu_initial": [[10,10]], '
            '"probabilite_propagation": 0.5}'
        )

        with pytest.raises(ConfigError, match="hors des limites"):
            ConfigLoader(str(config_file)).load()

    def test_negative_height_raises(self, tmp_path):
        """Une hauteur négative doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": -5, "largeur": 5, '
            '"positions_feu_initial": [[2,2]], '
            '"probabilite_propagation": 0.5}'
        )

        with pytest.raises(ConfigError, match="hauteur"):
            ConfigLoader(str(config_file)).load()

    def test_missing_file_raises(self):
        """Un fichier config inexistant doit lever ConfigError."""
        with pytest.raises(ConfigError, match="introuvable"):
            ConfigLoader("fichier_qui_nexiste_pas.json").load()

    def test_invalid_json_raises(self, tmp_path):
        """Un JSON syntaxiquement invalide doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text("{ceci n'est pas du json valide")

        with pytest.raises(ConfigError, match="JSON invalide"):
            ConfigLoader(str(config_file)).load()

    def test_negative_width_raises(self, tmp_path):
        """Une largeur négative doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": -3, '
            '"positions_feu_initial": [[2,2]], '
            '"probabilite_propagation": 0.5}'
        )
        with pytest.raises(ConfigError, match="largeur"):
            ConfigLoader(str(config_file)).load()

    def test_malformed_position_raises(self, tmp_path):
        """Une position qui n'est pas une paire [i, j] doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": 5, '
            '"positions_feu_initial": [[2, 2, 3]], '
            '"probabilite_propagation": 0.5}'
        )
        with pytest.raises(ConfigError, match="mal formée"):
            ConfigLoader(str(config_file)).load()

    def test_non_integer_coordinates_raises(self, tmp_path):
        """Des coordonnées non-entières doivent lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": 5, '
            '"positions_feu_initial": [["a", "b"]], '
            '"probabilite_propagation": 0.5}'
        )
        with pytest.raises(ConfigError, match="entiers"):
            ConfigLoader(str(config_file)).load()

    def test_empty_positions_list_raises(self, tmp_path):
        """Une liste de positions vide doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 5, "largeur": 5, '
            '"positions_feu_initial": [], '
            '"probabilite_propagation": 0.5}'
        )
        with pytest.raises(ConfigError, match="au moins une position"):
            ConfigLoader(str(config_file)).load()

    def test_grid_too_large_raises(self, tmp_path):
        """Une grille dépassant MAX_GRID_DIMENSION doit lever ConfigError."""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text(
            '{"hauteur": 1000, "largeur": 5, '
            '"positions_feu_initial": [[2,2]], '
            '"probabilite_propagation": 0.5}'
        )
        with pytest.raises(ConfigError, match="trop grande"):
            ConfigLoader(str(config_file)).load()

class TestStatisticalPropagation:

    def test_propagation_rate_matches_probability(self):
        """Sur de nombreux essais indépendants, le taux de propagation observé
        doit être statistiquement proche de p (loi des grands nombres).
        """
        p = 0.5
        n_trials = 2000
        propagated_count = 0

        for trial_seed in range(n_trials):
            # Grille minimale : une case en feu au centre, un seul voisin testé
            grid = Grid(h=3, l=1)
            grid.set_fire([(1, 0)])
            sim = Simulator(grid, p=p, seed=trial_seed)
            sim.step()

            # On vérifie si l'unique voisin du haut a pris feu
            if grid.state[0, 0] == ROUGE:
                propagated_count += 1

        observed_rate = propagated_count / n_trials

        # Tolérance de ±5% autour de p=0.5, large marge pour éviter un test flaky
        # tout en détectant une vraie erreur de logique (ex: bug de type <=)
        assert abs(observed_rate - p) < 0.05, (
            f"Taux observé {observed_rate:.3f} trop éloigné de p={p} "
            f"(sur {n_trials} essais)"
        )