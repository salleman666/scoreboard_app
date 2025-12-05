"""
PenaltyController
Handles penalty timing, Auto MV overlays, and GUI extraction
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple
from scoreboard_app.core.vmix_client import VMixClient


class PenaltyController:
    """
    Tracks penalty data and exposes it to GUI panels.
    Provides auto-timing and multi-view overlay support.
    """

    def __init__(self, vmix: VMixClient, cfg: dict):
        self.vmix = vmix
        self.cfg = cfg

        # penalty mapping path
        self.mapping = self.cfg["mapping"]["penalties"]

        # scoreboard input number
        self.scoreboard_input = self.cfg["inputs"]["scoreboard"]

        # background MV indexes (configurable later)
        self.mv_home = 9
        self.mv_away = 10

        self.overlay_home_on = False
        self.overlay_away_on = False

    # ---------------------------------------------------------------------
    # READ ALL PENALTIES FOR GUI
    # ---------------------------------------------------------------------

    def _read_penalty(self, side: str, slot: str) -> Dict[str, str]:
        """
        Reads one penalty slot (home or away, P1 or P2)
        Returns dict:
            {
                "number": "...",
                "name":   "...",
                "time":   "..."
            }
        """
        fields = self.mapping[side][slot]
        out = {}

        for name, vm_field in fields.items():
            try:
                value = self.vmix.get_text(self.scoreboard_input, vm_field)
                if value is None:
                    value = ""
                out[name] = value.strip()
            except Exception:
                out[name] = ""

        return out

    # ---------------------------------------------------------------------
    # REQUIRED BY PENALTY_PANEL
    # ---------------------------------------------------------------------

    def get_all_penalty_status(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Returns a 4-penalty structure for GUI:

        {
            "home": { "p1": {...}, "p2": {...} },
            "away": { "p1": {...}, "p2": {...} }
        }
        """
        return {
            "home": {
                "p1": self._read_penalty("home", "p1"),
                "p2": self._read_penalty("home", "p2"),
            },
            "away": {
                "p1": self._read_penalty("away", "p1"),
                "p2": self._read_penalty("away", "p2"),
            }
        }

    # ---------------------------------------------------------------------
    # AUTO OVERLAY LOGIC (OPTIONAL)
    # ---------------------------------------------------------------------

    def _time_to_seconds(self, t: str) -> int:
        """
        Converts "MM:SS" or "S" to total seconds.
        """
        if not t:
            return 0
        t = t.strip()

        if ":" in t:
            parts = t.split(":")
            if len(parts) == 2:
                try:
                    m = int(parts[0])
                    s = int(parts[1])
                    return m * 60 + s
                except ValueError:
                    return 0
        else:
            try:
                return int(t)
            except ValueError:
                return 0

        return 0

    def auto_refresh_mv(self):
        """
        Checks remaining times and toggles MV overlays on scoreboard input.
        Home: MV index 9
        Away: MV index 10
        """

        status = self.get_all_penalty_status()

        # HOME penalty alert
        h1 = self._time_to_seconds(status["home"]["p1"]["time"])
        h2 = self._time_to_seconds(status["home"]["p2"]["time"])
        has_home = (0 < h1 <= 5) or (0 < h2 <= 5)

        if has_home and not self.overlay_home_on:
            self.vmix.set_multiview_overlay_on(self.scoreboard_input, self.mv_home)
            self.overlay_home_on = True

        elif (not has_home) and self.overlay_home_on:
            self.vmix.set_multiview_overlay_off(self.scoreboard_input, self.mv_home)
            self.overlay_home_on = False

        # AWAY penalty alert
        a1 = self._time_to_seconds(status["away"]["p1"]["time"])
        a2 = self._time_to_seconds(status["away"]["p2"]["time"])
        has_away = (0 < a1 <= 5) or (0 < a2 <= 5)

        if has_away and not self.overlay_away_on:
            self.vmix.set_multiview_overlay_on(self.scoreboard_input, self.mv_away)
            self.overlay_away_on = True

        elif (not has_away) and self.overlay_away_on:
            self.vmix.set_multiview_overlay_off(self.scoreboard_input, self.mv_away)
            self.overlay_away_on = False
