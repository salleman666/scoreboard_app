# scoreboard_controller.py (Model B)

from __future__ import annotations
from typing import Dict, Any
from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.vmix_config import load_config


def _parse_mmss(text: str) -> int:
    """Returnerar sekunder."""
    try:
        m, s = text.strip().split(":")
        return int(m) * 60 + int(s)
    except:
        return 0


def _format_mmss(sec: int) -> str:
    if sec < 0: 
        sec = 0
    return f"{sec//60:02d}:{sec%60:02d}"


class ScoreboardController:
    """
    Model-B version: ren logik, ingen GUI-koppling.
    GUI anropar controller → controller skriver till vMix.
    """
    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg
        self.sb = cfg["scoreboard"]

        # Cache:
        self._last_state: Dict[str, Any] = {}

    # ---------------------------------------------------------
    # PUBLIC API (används av GUI)
    # ---------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """
        Läser scoreboard från vMix och returnerar som dictionary.
        """
        input_id = self.sb["input"]

        state = {}

        state["clock"] = self.client.get_text_field(input_id, self.sb["clock_field"])
        state["home_score"] = self.client.get_text_field(input_id, self.sb["home_score_field"])
        state["away_score"] = self.client.get_text_field(input_id, self.sb["away_score_field"])
        state["period"] = self.client.get_text_field(input_id, self.sb["period_field"])

        # Empty goal
        state["empty_home"] = self.client.get_text_field(input_id, self.sb["home_empty_field"])
        state["empty_away"] = self.client.get_text_field(input_id, self.sb["away_empty_field"])

        # Penalties lämnas åt penalty_controller

        self._last_state = state
        return state

    # ---------------------------------------------------------
    # CLOCK
    # ---------------------------------------------------------

    def adjust_clock(self, delta_sec: int):
        """Justera tid på scoreboard."""
        input_id = self.sb["input"]
        field = self.sb["clock_field"]

        current = self.client.get_text_field(input_id, field)
        sec = _parse_mmss(current)
        sec += delta_sec
        self.client.set_text(input_id, field, _format_mmss(sec))

    # ---------------------------------------------------------
    # SCORE
    # ---------------------------------------------------------

    def adjust_score(self, home: bool, delta: int):
        field = self.sb["home_score_field"] if home else self.sb["away_score_field"]
        input_id = self.sb["input"]

        try:
            val = int(self.client.get_text_field(input_id, field))
        except:
            val = 0

        val += delta
        if val < 0:
            val = 0

        self.client.set_text(input_id, field, str(val))

    # ---------------------------------------------------------
    # PERIOD
    # ---------------------------------------------------------

    def set_period(self, period: int):
        input_id = self.sb["input"]
        field = self.sb["period_field"]
        self.client.set_text(input_id, field, str(period))

    # ---------------------------------------------------------
    # EMPTY GOAL
    # ---------------------------------------------------------

    def set_empty_goal(self, home: bool, active: bool, text: str):
        """
        active=True → visa text och bakgrund
        active=False → rensa text och bakgrund
        """
        input_id = self.sb["input"]

        if home:
            field = self.sb["home_empty_field"]
            bg = self.sb["home_empty_bg_field"]
        else:
            field = self.sb["away_empty_field"]
            bg = self.sb["away_empty_bg_field"]

        if active:
            self.client.set_text(input_id, field, text)
            self.client.set_image(input_id, bg, bg)  # kräver GUI-mappning senare
        else:
            self.client.set_text(input_id, field, "")
            self.client.set_image(input_id, bg, "")

    # ---------------------------------------------------------
    # GOAL GRAPHICS
    # ---------------------------------------------------------

    def trigger_goal_graphic(self, home: bool):
        graphic = self.sb["goal_graphic_input"]
        channel = self.sb["goal_overlay_channel"]

        self.client.overlay_on(graphic, channel)

    def trigger_after_goal(self):
        graphic = self.sb["after_goal_graphic_input"]
        channel = self.sb["after_goal_overlay_channel"]
        duration_ms = self.sb["after_goal_duration_ms"]

        self.client.overlay_on(graphic, channel)
        return duration_ms

    # ---------------------------------------------------------
    # OVERLAY
    # ---------------------------------------------------------

    def toggle_scoreboard_overlay(self):
        input_id = self.sb["input"]
        ch = self.sb["overlay_channel"]

        active = self.client.is_overlay_active(input_id, ch)
        if active:
            self.client.overlay_off(ch)
            return False
        else:
            self.client.overlay_on(input_id, ch)
            return True
