"""
ShotsController
Handles updating home/away shots to the scoreboard input
using mappings defined in config/vmix_config.json.
"""

from __future__ import annotations
from typing import Optional
from scoreboard_app.core.vmix_client import VMixClient


class ShotsController:
    """
    Controls shots for home and away teams and writes values
    into scoreboard text fields in vMix.

    Uses config mappings:
      mapping.scoreboard.shots_home
      mapping.scoreboard.shots_away
    """

    def __init__(self, client: VMixClient, cfg: dict):
        self.client = client
        self.cfg = cfg

        self.scoreboard_input = cfg["inputs"]["scoreboard"]

        self.map_home = cfg["mapping"]["scoreboard"]["shots_home"]
        self.map_away = cfg["mapping"]["scoreboard"]["shots_away"]

        self._shots_home = 0
        self._shots_away = 0

    # ------------- STATE -------------------------------------

    def get_home(self) -> int:
        return self._shots_home

    def get_away(self) -> int:
        return self._shots_away

    # ------------- MUTATION ----------------------------------

    def inc_home(self, n: int = 1):
        self._shots_home += n
        self._sync_home()

    def inc_away(self, n: int = 1):
        self._shots_away += n
        self._sync_away()

    def reset(self):
        self._shots_home = 0
        self._shots_away = 0
        self._sync_home()
        self._sync_away()

    # ------------- SYNC TO VMIX ------------------------------

    def _sync_home(self):
        try:
            self.client.set_text(
                self.scoreboard_input,
                self.map_home,
                str(self._shots_home)
            )
        except Exception as e:
            print(f"[ShotsController] FAIL update home shots: {e}")

    def _sync_away(self):
        try:
            self.client.set_text(
                self.scoreboard_input,
                self.map_away,
                str(self._shots_away)
            )
        except Exception as e:
            print(f"[ShotsController] FAIL update away shots: {e}")
