import logging

log = logging.getLogger(__name__)


class ClockController:
    """
    Master match clock controller.
    Supports:
        SetCountdown
        StartCountdown
        PauseCountdown
        StopCountdown
        AdjustCountdown
    """

    def __init__(self, client, cfg):
        """
        client -> VMixClient
        cfg -> full config dict with mapping.clock
        """
        self.client = client
        self.cfg = cfg

        # load mapping
        self.mapping = cfg["mapping"]["clock"]
        self.clock_input = self.mapping.get("input")
        self.clock_field = self.mapping.get("field")

        # runtime state
        self.running = False

    # ======================================================
    # SAFETY WRAPPER
    # ======================================================
    def _ensure_valid(self) -> bool:
        if not self.clock_input or not self.clock_field:
            log.error("[CLOCK] Missing mapping: cannot run")
            return False
        return True

    def _safe_call(self, fn):
        """
        wrapper to catch vMix issues without crashing GUI
        """
        try:
            fn()
        except Exception as e:
            log.error(f"[CLOCK] VMix operation failed: {e}")

    # ======================================================
    # CORE OPERATIONS
    # ======================================================
    def set_time(self, value: str):
        """
        Set new countdown value e.g. '20:00'
        """
        if not self._ensure_valid():
            return

        def go():
            self.client.set_countdown(self.clock_input, self.clock_field, value)

        self._safe_call(go)

    def start(self):
        """
        Start or resume the match clock.
        "StartCountdown" must be used when clock is idle/reset.
        """
        if not self._ensure_valid():
            return

        def go():
            self.client.start_countdown(self.clock_input, self.clock_field)

        self._safe_call(go)
        self.running = True

    def pause(self):
        """
        Pause the match clock.
        """
        if not self._ensure_valid():
            return

        def go():
            self.client.pause_countdown(self.clock_input, self.clock_field)

        self._safe_call(go)
        self.running = False

    def stop(self):
        """
        End period — fully reset to configured value.
        StopCountdown will restore field to StartTime defined in GT title.
        """
        if not self._ensure_valid():
            return

        def go():
            self.client.stop_countdown(self.clock_input, self.clock_field)

        self._safe_call(go)
        self.running = False

    def adjust(self, seconds: int):
        """
        Adjust +/- seconds from current running time
        Can be used during play or paused states.
        """
        if not self._ensure_valid():
            return

        def go():
            self.client.adjust_countdown(self.clock_input, self.clock_field, seconds)

        self._safe_call(go)

    # ======================================================
    # UI EVENT HELPERS
    # ======================================================
    def toggle_pause(self):
        """
        Unified button:
        If running → pause
        If paused → start
        """
        if not self._ensure_valid():
            return

        if self.running:
            self.pause()
        else:
            self.start()
