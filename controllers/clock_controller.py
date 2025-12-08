import time
import threading
import logging


class ClockController:
    """
    Handles match countdown + penalty countdown sync.

    Mapping required in config:
        clock.input
        clock.field
        clock.start_value

    Penalty mapping must be:
        penalties.input
        penalties.home1.time
        penalties.home2.time
        penalties.away1.time
        penalties.away2.time

    All .Text fields support:
        SetCountdown
        StartCountdown
        PauseCountdown
        StopCountdown
        AdjustCountdown
    """

    def __init__(self, vmix_client, cfg: dict):
        self.client = vmix_client
        self.cfg = cfg

        c = cfg.get("clock", {})
        self.clock_input = c.get("input", "")
        self.clock_field = c.get("field", "")
        self.default_start = c.get("start_value", "20:00")

        p = cfg.get("penalties", {})
        self.pen_input = p.get("input", "")
        self.pen_slots = {
            "home1": p.get("home1", {}),
            "home2": p.get("home2", {}),
            "away1": p.get("away1", {}),
            "away2": p.get("away2", {}),
        }

        self.running = False
        self._period_index = 1  # GUI may use this later

        logging.info("[CLOCK] Ready with countdown sync")

    # ---------------------------------------------------------------------
    # LOW-LEVEL UTILS
    # ---------------------------------------------------------------------
    def _start(self, input_name, field):
        self.client.start_countdown_full(input_name, field)

    def _pause(self, input_name, field):
        self.client.pause_countdown_full(input_name, field)

    def _stop(self, input_name, field):
        self.client.stop_countdown_full(input_name, field)

    def _set_time(self, input_name, field, value):
        self.client.set_countdown_full(input_name, field, value)

    def _adjust(self, input_name, field, seconds: int):
        self.client.adjust_countdown_full(input_name, field, seconds)

    # ---------------------------------------------------------------------
    # PENALTY HELPERS
    # ---------------------------------------------------------------------
    def _slot_fields(self):
        """
        Return active penalty fields as list of field names to control.
        """
        out = []
        for slot, data in self.pen_slots.items():
            f = data.get("time", "")
            if f:
                out.append(f)
        return out

    # ---------------------------------------------------------------------
    # MAIN CLOCK OPERATIONS
    # ---------------------------------------------------------------------
    def start_clock(self):
        """
        - First start match countdown
        - Then resume any penalty timers
        """
        if not self.clock_input or not self.clock_field:
            logging.error("[CLOCK] Missing mapping: cannot start")
            return

        # Set start time before first start if needed
        self._set_time(self.clock_input, self.clock_field, self.default_start)

        self._start(self.clock_input, self.clock_field)
        self.running = True

        # resume penalties
        for f in self._slot_fields():
            self._start(self.pen_input, f)

        logging.info("[CLOCK] started + penalty sync")

    def pause_clock(self):
        """
        Pause main countdown AND all active penalties
        """
        if not self.clock_input or not self.clock_field:
            logging.error("[CLOCK] Missing mapping: cannot pause")
            return

        self._pause(self.clock_input, self.clock_field)

        for f in self._slot_fields():
            self._pause(self.pen_input, f)

        self.running = False
        logging.info("[CLOCK] paused + penalty sync")

    def stop_clock(self):
        """
        End of period:
        - Stop main countdown (reset to default)
        - Pause penalties (don't reset penalties)
        """
        if not self.clock_input or not self.clock_field:
            logging.error("[CLOCK] Missing mapping: cannot stop")
            return

        # full stop resets time to initial
        self._stop(self.clock_input, self.clock_field)

        # penalties only PAUSE (never STOP)
        for f in self._slot_fields():
            self._pause(self.pen_input, f)

        self.running = False
        logging.info("[CLOCK] stopped + penalty sync")

    def adjust_time(self, seconds):
        """
        +/- seconds adjustment on main match clock
        """
        if not self.clock_input or not self.clock_field:
            logging.error("[CLOCK] Missing mapping: cannot adjust")
            return

        self._adjust(self.clock_input, self.clock_field, seconds)
        logging.info(f"[CLOCK] adjust {seconds} seconds")

    # ---------------------------------------------------------------------
    # OPTIONAL PERIOD NAME
    # ---------------------------------------------------------------------
    def set_period(self, index: int):
        """
        Just remember value. GUI may display it later.
        """
        self._period_index = index
        logging.info(f"[CLOCK] period set to {index}")

    # ---------------------------------------------------------------------
    # THREAD AUTO READ (OPTIONAL)
    # ---------------------------------------------------------------------
    def start_auto_read(self, interval_ms=200):
        """
        OPTIONAL background status polling
        We can auto-update GUI labels if needed.
        """
        def loop():
            while True:
                try:
                    status = self.client.get_status()
                    # GUI read if needed later
                except:
                    pass
                time.sleep(interval_ms / 1000)

        t = threading.Thread(target=loop, daemon=True)
        t.start()
