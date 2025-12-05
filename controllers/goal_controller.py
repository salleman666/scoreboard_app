"""
GoalController module
---------------------

Ansvar:
- Hantera mål-logik (home / away)
- Uppdatera scoreboard-fält i vMix
- Trigga after-goal grafik (om aktiverat)
- Hantera empty-goal states

Denna controller:
- håller ingen GUI logik
- kastar tydliga fel när vMix saknar fält
- läser fältnamn från config
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from scoreboard_app.core.vmix_client import VMixClient


class GoalController:
    """
    Controller för mål-logik
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        """
        :param client: VMixClient som hanterar vMix API-kommunikation
        :param cfg: konfigurationsobjekt enligt vmix_config.json
        """
        self.client = client
        self.cfg = cfg

        # score state
        self.home_goals = 0
        self.away_goals = 0

        # empty-goal flaggar
        self.home_empty = False
        self.away_empty = False

    # ----------------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------------

    def _get_field(self, side: str, field: str) -> str:
        """
        Returnerar fältnamn från konfigurering
        :param side: "home" eller "away"
        :param field: t.ex. "score_field"
        """
        try:
            return self.cfg["goal"][side][field]
        except Exception as e:
            raise ValueError(
                f"GoalController missing config field for {side}.{field}: {e}"
            )

    def _update_scoreboard_field(self, side: str, value: str) -> None:
        """
        Sätter score-fält i scoreboard graphic
        """
        field_name = self._get_field(side, "score_field")
        input_key = self.cfg["goal"]["scoreboard_input"]

        try:
            self.client.set_text(input_key, field_name, value)
        except Exception as e:
            raise RuntimeError(
                f"Failed to set {side} scoreboard field '{field_name}' "
                f"to '{value}': {e}"
            )

    # ----------------------------------------------------------------------
    # PUBLIC API — USED BY GUI
    # ----------------------------------------------------------------------

    def goal_home(self, after_graphic: bool = True) -> None:
        """
        Registrerar hemmamål, uppdaterar scoreboard
        """
        self.home_goals += 1
        self._update_scoreboard_field("home", str(self.home_goals))

        if after_graphic:
            self._show_after_goal_graphic("home")

    def goal_away(self, after_graphic: bool = True) -> None:
        """
        Registrerar bortamål, uppdaterar scoreboard
        """
        self.away_goals += 1
        self._update_scoreboard_field("away", str(self.away_goals))

        if after_graphic:
            self._show_after_goal_graphic("away")

    # ----------------------------------------------------------------------

    def toggle_empty_goal(self, side: str) -> None:
        """
        Växlar empty-goal state och sätter rätt grafik
        :param side: "home" eller "away"
        """

        if side == "home":
            self.home_empty = not self.home_empty
            self._update_empty_goal("home", self.home_empty)

        elif side == "away":
            self.away_empty = not self.away_empty
            self._update_empty_goal("away", self.away_empty)

        else:
            raise ValueError("toggle_empty_goal: side must be 'home' or 'away'")

    # ----------------------------------------------------------------------

    def _update_empty_goal(self, side: str, state: bool) -> None:
        """
        Sätter empty-goal grafik ON/OFF för rätt lag
        """

        field_name = self._get_field(side, "empty_goal_field")
        input_key = self.cfg["goal"]["scoreboard_input"]

        value = "ON" if state else "OFF"

        try:
            self.client.set_text(input_key, field_name, value)
        except Exception as e:
            raise RuntimeError(
                f"Failed to set empty-goal for {side}: {e}"
            )

    # ----------------------------------------------------------------------

    def _show_after_goal_graphic(self, side: str) -> None:
        """
        Triggar after-goal graphic om aktiverat i config
        """

        if not self.cfg["goal"].get("after_goal_enabled", False):
            return

        graphic_key = self.cfg["goal"]["after_goal_input"]

        try:
            self.client.overlay_show(graphic_key)
        except Exception as e:
            raise RuntimeError(
                f"After-goal graphic failed for {side}: {e}"
            )
