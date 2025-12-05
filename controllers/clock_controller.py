from __future__ import annotations
from typing import Any, Dict

from scoreboard_app.core.vmix_client import VMixClient


class ClockController:
    """
    Controls the period and match clock inside a scoreboard GT input.
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg

        # --------------------------------------------
        # INPUT + FIELD MAPPING FROM CONFIG
        # --------------------------------------------
        try:
            sc = cfg["inputs"]["scoreboard"]                     # input key
            mp = cfg["mapping"]["scoreboard"]                    # mapping keys
            self.clock_field = mp["clock"]
            self.period_field = mp["period"]
        except Exception:
            raise KeyError(
                "ClockController: your config.json is missing scoreboard.clock or scoreboard.period mapping"
            )

        self.scoreboard_input = sc

        # refresh delay (optional)
        self.delay_ms = cfg["defaults"].get("clock_refresh_ms", 500)

    # ========================================================================
    # BASICS — CLOCK CONTROL
    # ========================================================================

    def start_clock(self) -> None:
        """
        Starts the countdown timer in the scoreboard.
        """
        try:
            self.client.set_countdown_start(
                input_name=self.scoreboard_input,
                field_name=self.clock_field,
            )
        except Exception as e:
            print("[ClockController] start_clock ERROR:", e)

    def stop_clock(self) -> None:
        """
        Pauses the countdown timer.
        """
        try:
            self.client.set_countdown_pause(
                input_name=self.scoreboard_input,
                field_name=self.clock_field,
            )
        except Exception as e:
            print("[ClockController] stop_clock ERROR:", e)

    def reset_clock(self, seconds: int | None = None) -> None:
        """
        Reset to a specific total time or default period length.

        If seconds is None -> resets to period default in config.
        """
        try:
            if seconds is None:
                period_minutes = int(self.cfg["defaults"].get("period_minutes", 20))
                seconds = period_minutes * 60

            self.client.set_text(
                input_name=self.scoreboard_input,
                field_name=self.clock_field,
                value=self._format_seconds(seconds),
            )

            # reset countdown engine inside vMix
            self.client.set_countdown_reset(
                input_name=self.scoreboard_input,
                field_name=self.clock_field,
            )

        except Exception as e:
            print("[ClockController] reset_clock ERROR:", e)

    # ========================================================================
    # PERIOD CONTROL
    # ========================================================================

    def set_period(self, period_index: int) -> None:
        """
        Update the period field in the scoreboard.

        GUI calls: period_index = 1, 2, 3, 4...
        """
        try:
            self.client.set_text(
                input_name=self.scoreboard_input,
                field_name=self.period_field,
                value=str(period_index),
            )
        except Exception as e:
            print("[ClockController] set_period ERROR:", e)

    # ========================================================================
    # CLOCK TEXT ACCESS
    # ========================================================================

    def get_clock_text(self) -> str:
        """
        Returns current clock text, like '12:33' or '' if missing.
        """
        try:
            value = self.client.get_text(
                input_name=self.scoreboard_input,
                field_name=self.clock_field,
            )
            return value or ""
        except Exception:
            return ""

    # ========================================================================
    # HELPER
    # ========================================================================

    @staticmethod
    def _format_seconds(total: int) -> str:
        """
        Converts seconds → mm:ss format
        """
        m = total // 60
        s = total % 60
        return f"{m:02}:{s:02}"
