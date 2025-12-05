import logging
from typing import Any, Dict

from scoreboard_app.core.vmix_client import VMixClient

logger = logging.getLogger(__name__)


class ClockController:
    """
    Controls scoreboard match clock.

    Reads mapping from config:
        cfg["mapping"]["scoreboard"]["clock"]
        cfg["mapping"]["scoreboard"]["period"]
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg

        self.input_name = cfg["inputs"]["scoreboard"]
        m = cfg["mapping"]["scoreboard"]

        self.clock_field = m["clock"]
        self.period_field = m["period"]

    # ---------------------------------------------------
    # BASIC CLOCK FUNCTIONS
    # ---------------------------------------------------
    def start_clock(self) -> None:
        try:
            self.client.call_function(
                "StartCountdown",
                Input=self.input_name,
                SelectedName=self.clock_field
            )
        except Exception as e:
            logger.error("[ClockController] start_clock ERROR: %s", e)

    def stop_clock(self) -> None:
        try:
            self.client.call_function(
                "PauseCountdown",
                Input=self.input_name,
                SelectedName=self.clock_field
            )
        except Exception as e:
            logger.error("[ClockController] stop_clock ERROR: %s", e)

    def reset_clock(self) -> None:
        try:
            self.client.call_function(
                "ResetCountdown",
                Input=self.input_name,
                SelectedName=self.clock_field
            )
        except Exception as e:
            logger.error("[ClockController] reset_clock ERROR: %s", e)

    # ---------------------------------------------------
    # PERIOD HANDLING
    # ---------------------------------------------------
    def set_period(self, period_index: int) -> None:
        """
        Update TITLE field
        """
        try:
            self.client.set_text(
                self.input_name,
                self.period_field,
                str(period_index)
            )
        except Exception as e:
            logger.error("[ClockController] set_period ERROR: %s", e)

    # ---------------------------------------------------
    # GETTERS
    # ---------------------------------------------------
    def get_time(self) -> str:
        """
        Reads current time text from scoreboard clock
        """
        try:
            return self.client.get_text(
                self.input_name,
                self.clock_field
            )
        except Exception:
            return ""
