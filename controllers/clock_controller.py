"""
ClockController
----------------

Ansvar:
- Starta / stoppa / pausa matchklockan
- Återställa periodtid
- Hantera overtime
- Uppdatera scoreboard-inputs med aktuell tid
- All vMix-interaktion via VMixClient
"""

from __future__ import annotations
from typing import Optional, Dict, Any

from scoreboard_app.core.vmix_client import VMixClient


class ClockController:
    """
    Kontrollerar matchklockan i vMix.

    All XML/HTTP talk sker enbart genom VMixClient.
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg

        # pointers till fält i scoreboard
        self.scoreboard_input_name = cfg["scoreboard"]["input"]
        self.period_field = cfg["scoreboard"]["fields"]["period"]
        self.clock_field = cfg["scoreboard"]["fields"]["clock"]

        # standardvärden
        self.default_period_time: str = cfg["clock"].get("default_period_time", "20:00")
        self.overtime_time: str = cfg["clock"].get("default_overtime_time", "05:00")

    # -----------------------------------------------------------------
    # EXPOSED ACTIONS
    # -----------------------------------------------------------------

    def start(self) -> bool:
        """Starta matchklockan."""
        return self.client.set_clock_running(True)

    def stop(self) -> bool:
        """Stoppa matchklockan."""
        return self.client.set_clock_running(False)

    def reset_period(self) -> bool:
        """Återställ klockan till periodens originaltid."""
        return self.set_time(self.default_period_time)

    def reset_overtime(self) -> bool:
        """Återställ klockan till overtime-standard."""
        return self.set_time(self.overtime_time)

    # -----------------------------------------------------------------

    def toggle(self) -> bool:
        """
        Start/Stop toggle baserat på status från vMix.
        """
        running = self.client.get_clock_running()
        return self.client.set_clock_running(not running)

    # -----------------------------------------------------------------

    def set_time(self, mmss: str) -> bool:
        """
        Sätt klockan till ett specificerat MM:SS värde.
        """
        ok = self.client.set_clock_time(mmss)
        if ok:
            self.refresh_scoreboard_time()
        return ok

    # -----------------------------------------------------------------

    def set_scoreboard_period(self, value: str) -> bool:
        """
        Uppdatera periodfältet i scoreboardgrafiken.
        """
        return self.client.set_text(
            input_name=self.scoreboard_input_name,
            field_name=self.period_field,
            value=value,
        )

    # -----------------------------------------------------------------

    def refresh_scoreboard_time(self) -> bool:
        """
        Läs nuvarande klocktid från vMix och uppdatera scoreboard-grafiken.
        """
        time_str = self.client.get_clock_time()
        return self.client.set_text(
            input_name=self.scoreboard_input_name,
            field_name=self.clock_field,
            value=time_str,
        )

    # -----------------------------------------------------------------

    def full_refresh(self):
        """
        Force-refresh av alla grafiska fält kopplade till klockan.
        """
        self.refresh_scoreboard_time()
