import json
import logging
from pathlib import Path
from scoreboard_app.core.vmix_client import VMixClient


class ClockController:
    """
    Handles game time logic and communicates with vMix via VMixClient.
    GUI should only call these methods.
    """

    def __init__(self, vmix_client=None, config_path=None):
        """
        GUI calls ClockController(self.client, self.cfg)

        Therefore:
        - vmix_client = VMixClient instance
        - config_path = already loaded JSON dict
        """

        # ---------------------------------------------------------
        # VMIX CLIENT depends first
        # ---------------------------------------------------------
        self.vmix = vmix_client if vmix_client else VMixClient()

        # ---------------------------------------------------------
        # CONFIG HANDLING
        # ---------------------------------------------------------
        if isinstance(config_path, dict):
            # CONFIG ALREADY LOADED — BEST CASE
            self.config = config_path

        else:
            # Fall back to file loading
            if config_path is None:
                config_path = Path(__file__).resolve().parents[1] / "config" / "vmix_config.json"

            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

        # Extract mapped clock fields
        clock_cfg = self.config.get("clock", {})
        self.input_name = clock_cfg.get("input")
        self.field_name = clock_cfg.get("field")
        self.source_type = clock_cfg.get("source_type", "countdown")

        # Local state
        self.period_index = 1
        self.period_durations = {
            1: 20 * 60,
            2: 20 * 60,
            3: 20 * 60,
            4: 5 * 60,
        }

    # ---------------------------------------------------------
    # INTERNAL UTILITY
    # ---------------------------------------------------------

    def _apply_mapping(self, fn, **kwargs):
        if not self.input_name:
            logging.error("[CLOCK] Missing vMix mapping: clock.input")
            return False

        return fn(self.input_name, **kwargs)

    # ---------------------------------------------------------
    # CLOCK CONTROL
    # ---------------------------------------------------------

    def start_clock(self):
        logging.info("[CLOCK] Start")
        return self._apply_mapping(self.vmix.start_countdown)

    def stop_clock(self):
        logging.info("[CLOCK] Pause")
        return self._apply_mapping(self.vmix.pause_countdown)

    def reset_clock(self):
        duration = self.period_durations.get(self.period_index, 20 * 60)
        logging.info(f"[CLOCK] Reset → {duration}s")
        return self._apply_mapping(self.vmix.set_countdown, duration_seconds=duration)

    # ---------------------------------------------------------
    # ADJUSTMENTS
    # ---------------------------------------------------------

    def increase_time(self, seconds=1):
        logging.info(f"[CLOCK] +{seconds}s")
        return self._apply_mapping(self.vmix.adjust_countdown, seconds=seconds)

    def decrease_time(self, seconds=1):
        logging.info(f"[CLOCK] -{seconds}s")
        return self._apply_mapping(self.vmix.adjust_countdown, seconds=-seconds)

    # ---------------------------------------------------------
    # PERIOD HANDLING
    # ---------------------------------------------------------

    def set_period(self, period_index):
        logging.info(f"[CLOCK] Set period → {period_index}")
        self.period_index = period_index
        return self.reset_clock()

    # ---------------------------------------------------------
    # PERIOD TEXT (optional)
    # ---------------------------------------------------------

    def update_period_text(self, text):
        field = self.config.get("clock", {}).get("period_field")
        if not field:
            return False

        return self.vmix.set_text(
            input_name=self.input_name,
            field_name=field,
            value=text,
        )

    # ---------------------------------------------------------
    # PENALTY SYNC HOOKS (placeholder)
    # ---------------------------------------------------------

    def sync_penalties_on_start(self):
        pass

    def sync_penalties_on_stop(self):
        pass
