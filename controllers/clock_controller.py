import time
from typing import Dict
from scoreboard_app.core.vmix_client import VMixClient


class ClockController:
    """
    Handles match clock logic and communication with the vMix scoreboard graphic.
    """

    def __init__(self, client: VMixClient, cfg: Dict):
        self.client = client
        self.cfg = cfg

        # NEW: scoreboard input ID from config
        self.scoreboard_input = cfg["inputs"]["scoreboard"]

        # NEW: field mapping from config (correct location)
        self.clock_field = cfg["mapping"]["scoreboard"]["clock"]
        self.period_field = cfg["mapping"]["scoreboard"]["period"]

        # refresh timing from config
        self.refresh_ms = cfg["defaults"]["clock_refresh_ms"]


    # ------------------------------------------------------------
    def update_clock(self, clock_text: str):
        """
        Update the visible game clock on the scoreboard.
        """

        if not self.scoreboard_input:
            raise RuntimeError("No scoreboard input configured")

        self.client.set_text(
            input_key=self.scoreboard_input,
            field_name=self.clock_field,
            value=clock_text,
        )


    # ------------------------------------------------------------
    def update_period(self, period_text: str):
        """
        Update the visible match period.
        """

        if not self.scoreboard_input:
            raise RuntimeError("No scoreboard input configured")

        self.client.set_text(
            input_key=self.scoreboard_input,
            field_name=self.period_field,
            value=period_text,
        )


    # ------------------------------------------------------------
    def auto_refresh_loop(self, generator_fn):
        """
        Run a loop where generator_fn() yields new clock values (ex: countdown logic)

        generator_fn must return: (clock_text, period_text)
        """

        while True:
            clock_str, period_str = generator_fn()

            if clock_str is not None:
                self.update_clock(clock_str)

            if period_str is not None:
                self.update_period(period_str)

            time.sleep(self.refresh_ms / 1000.0)
