"""
ScoreboardController
- Central controller for scoreboard state (goals, period, shots, time)
- Uses VMixClient for all vMix communication
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.vmix_config import load_config


class ScoreboardController:
    """
    The master state controller for:
    - goals
    - shots
    - logos
    - team names
    - period
    - scoreboard text fields

    All writes go ONLY through vmix_client.set_text or set_image.
    """

    def __init__(self, client: VMixClient, cfg: Optional[Dict[str, Any]] = None):
        self.client = client
        self.cfg = cfg if cfg else load_config()

        # cached state (NOT required, but convenient)
        self.home_score = 0
        self.away_score = 0
        self.shots_home = 0
        self.shots_away = 0
        self.period = 1

        # mapping extracted for convenience
        self.input_scoreboard = self.cfg["inputs"].get("scoreboard", "")
        self.mapping = self.cfg["mapping"]["scoreboard"]

    # ------------------------------------------------------------
    # SCORE CONTROL
    # ------------------------------------------------------------

    def set_home_score(self, value: int) -> None:
        self.home_score = value
        self._write(self.mapping["home_score"], str(value))

    def set_away_score(self, value: int) -> None:
        self.away_score = value
        self._write(self.mapping["away_score"], str(value))

    def add_goal_home(self) -> None:
        self.home_score += 1
        self.set_home_score(self.home_score)

    def add_goal_away(self) -> None:
        self.away_score += 1
        self.set_away_score(self.away_score)

    # ------------------------------------------------------------
    # SHOTS
    # ------------------------------------------------------------

    def set_shots_home(self, value: int) -> None:
        self.shots_home = value
        self._write(self.mapping["shots_home"], str(value))

    def set_shots_away(self, value: int) -> None:
        self.shots_away = value
        self._write(self.mapping["shots_away"], str(value))

    def add_shot_home(self) -> None:
        self.shots_home += 1
        self.set_shots_home(self.shots_home)

    def add_shot_away(self) -> None:
        self.shots_away += 1
        self.set_shots_away(self.shots_away)

    # ------------------------------------------------------------
    # PERIOD
    # ------------------------------------------------------------

    def set_period(self, value: int) -> None:
        self.period = value
        self._write(self.mapping["period"], str(value))

    # ------------------------------------------------------------
    # TEAM REFS
    # ------------------------------------------------------------

    def set_home_name(self, text: str) -> None:
        self._write(self.mapping["home_name"], text)

    def set_away_name(self, text: str) -> None:
        self._write(self.mapping["away_name"], text)

    def set_home_logo(self, path: str) -> None:
        self._write(self.mapping["home_logo"], path, is_image=True)

    def set_away_logo(self, path: str) -> None:
        self._write(self.mapping["away_logo"], path, is_image=True)

    # ------------------------------------------------------------
    # INTERNAL — single field write
    # ------------------------------------------------------------

    def _write(self, field_name: str, value: str, is_image: bool = False) -> None:
        """
        Generic value writer
        """
        if not self.input_scoreboard or not field_name:
            return

        try:
            if is_image:
                self.client.set_image(self.input_scoreboard, field_name, value)
            else:
                self.client.set_text(self.input_scoreboard, field_name, value)
        except Exception as e:
            print(f"[ScoreboardController] WRITE ERROR: {field_name} -> {e}")
