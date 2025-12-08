import logging
from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.core.config_loader import load_config, save_config

log = logging.getLogger(__name__)


class ClockController:
    """
    Central logic for main game clock.

    RULES:
    - start_countdown  = first start (from initial value)
    - pause_countdown  = toggle play/pause without resetting
    - stop_countdown   = reset to initial value (only used at period end)
    - adjust           = Add/Sub seconds during live play
    """

    def __init__(self, client: VMixClient, cfg=None):
        self.client = client
        self.cfg = cfg if cfg else load_config()

        # -----------------------
        # ENSURE CONFIG STRUCTURE
        # -----------------------
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        if "clock" not in self.cfg["mapping"]:
            self.cfg["mapping"]["clock"] = {}

        clock_map = self.cfg["mapping"]["clock"]

        # guarantee mapping fields exist
        clock_map.setdefault("input", "")
        clock_map.setdefault("field", "")
        clock_map.setdefault("initial_time", "20:00")      # default
        clock_map.setdefault("period_1", "20:00")
        clock_map.setdefault("period_2", "20:00")
        clock_map.setdefault("period_3", "20:00")
        clock_map.setdefault("overtime", "05:00")

        save_config(self.cfg)

        # local state
        self.clock_input = clock_map["input"]          # SCOREBOARD UPPE
        self.clock_field = clock_map["field"]          # Time.Text
        self.initial_time = clock_map["initial_time"]
        self.running = False

    # -------------------------------------------------------------
    # INTERNAL UTILITY
    # -------------------------------------------------------------
    def _has_mapping(self):
        if not self.clock_input or not self.clock_field:
            log.error("[CLOCK] Missing mapping: cannot run")
            return False
        return True

    # -------------------------------------------------------------
    # CLOCK ACTIONS
    # -------------------------------------------------------------
    def start(self):
        """
        First launch of a period — ALWAYS set the time before start.
        """
        if not self._has_mapping():
            return

        if not self.running:
            # first start = load initial time
            self.client.set_countdown(
                self.clock_input,
                self.clock_field,
                self.initial_time
            )
            self.client.start_countdown(
                self.clock_input,
                self.clock_field
            )
            self.running = True
            log.info("[CLOCK] started")
        else:
            # already running => ignore
            log.info("[CLOCK] already running")

    def toggle_pause(self):
        """
        Play/Pause without resetting.
        """
        if not self._has_mapping():
            return

        if not self.running:
            # resume
            self.client.start_countdown(
                self.clock_input,
                self.clock_field
            )
            self.running = True
            log.info("[CLOCK] resumed")
        else:
            # pause
            self.client.pause_countdown(
                self.clock_input,
                self.clock_field
            )
            self.running = False
            log.info("[CLOCK] paused")

    def stop(self):
        """
        Reset clock to initial time — only at period end!
        """
        if not self._has_mapping():
            return

        self.client.stop_countdown(
            self.clock_input,
            self.clock_field
        )
        self.running = False
        log.info("[CLOCK] stopped/reset")

    # -------------------------------------------------------------
    # PERIOD SWITCHING
    # -------------------------------------------------------------
    def set_period(self, period_index: int):
        """
        0 = P1, 1 = P2, 2 = P3, 3 = OT
        """
        if not self._has_mapping():
            return

        m = self.cfg["mapping"]["clock"]

        if period_index == 0:
            new_time = m.get("period_1", "20:00")
        elif period_index == 1:
            new_time = m.get("period_2", "20:00")
        elif period_index == 2:
            new_time = m.get("period_3", "20:00")
        else:
            new_time = m.get("overtime", "05:00")

        # store & save
        self.initial_time = new_time
        m["initial_time"] = new_time
        save_config(self.cfg)

        # reset VMIX countdown
        self.client.set_countdown(
            self.clock_input,
            self.clock_field,
            new_time
        )
        self.running = False
        log.info(f"[CLOCK] period={period_index} new time={new_time}")

    # -------------------------------------------------------------
    # IN-GAME ADJUSTMENTS
    # -------------------------------------------------------------
    def adjust(self, delta_sec: int):
        """
        +/- seconds while running or paused.
        """
        if not self._has_mapping():
            return

        self.client.adjust_countdown(
            self.clock_input,
            self.clock_field,
            delta_sec
        )
        log.info(f"[CLOCK] adjust: {delta_sec:+d} sec")

    # -------------------------------------------------------------
    # FUTURE: PENALTY SYNC (activated later)
    # -------------------------------------------------------------
    def sync_penalties_resume(self):
        """ Called when clock resumes — pause all active penalties """
        pass

    def sync_penalties_pause(self):
        """ Called when clock pauses — resume all active penalties """
        pass

    def sync_penalties_stop(self):
        """ Called when period stops — reset penalties """
        pass
