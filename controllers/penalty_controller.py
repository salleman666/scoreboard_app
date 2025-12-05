import threading
import time
from typing import Dict, Any


class PenaltyController:
    """
    Automatic penalty monitoring controller.
    Designed for SCOREBOARD UPPE where penalty time and graphics
    are located.
    """

    def __init__(self, client, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg

        # input name
        self.penalty_input = cfg["inputs"]["penalty"]

        mapping = cfg["mapping"]["penalties"]

        # ---------------- HOME ----------------
        self.h1_time_field = mapping["home"]["p1"]["time"]
        self.h1_nr_field = mapping["home"]["p1"]["number"]
        self.h1_bg_field = mapping["home"]["p1"]["bg"]
        self.h1_nr_bg_field = mapping["home"]["p1"]["nr_bg"]

        self.h2_time_field = mapping["home"]["p2"]["time"]
        self.h2_nr_field = mapping["home"]["p2"]["number"]
        self.h2_bg_field = mapping["home"]["p2"]["bg"]
        self.h2_nr_bg_field = mapping["home"]["p2"]["nr_bg"]

        # ---------------- AWAY ----------------
        self.a1_time_field = mapping["away"]["p1"]["time"]
        self.a1_nr_field = mapping["away"]["p1"]["number"]
        self.a1_bg_field = mapping["away"]["p1"]["bg"]
        self.a1_nr_bg_field = mapping["away"]["p1"]["nr_bg"]

        self.a2_time_field = mapping["away"]["p2"]["time"]
        self.a2_nr_field = mapping["away"]["p2"]["number"]
        self.a2_bg_field = mapping["away"]["p2"]["bg"]
        self.a2_nr_bg_field = mapping["away"]["p2"]["nr_bg"]

        # start background thread
        self._loop_running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    # ===============================================================
    def _read_seconds(self, text: str) -> int:
        """Convert 01:45 -> 105 seconds"""
        if not text:
            return 0

        text = text.strip()

        if ":" not in text:
            try:
                return int(text)
            except:
                return 0

        m, s = text.split(":")
        try:
            return int(m) * 60 + int(s)
        except:
            return 0

    # ===============================================================
    def _handle_slot(self, time_field, nr_field, bg_field, nr_bg_field):
        """
        Check one penalty slot and automatically show/hide
        text and backgrounds.
        """

        t = self.client.get_text(self.penalty_input, time_field)
        seconds = self._read_seconds(t)

        visible = seconds > 0

        # time text
        self.client.set_text_visible_on_or_off(self.penalty_input, time_field, visible)
        # number text
        self.client.set_text_visible_on_or_off(self.penalty_input, nr_field, visible)
        # backgrounds
        self.client.set_bg_visible_on_or_off(self.penalty_input, bg_field, visible)
        self.client.set_bg_visible_on_or_off(self.penalty_input, nr_bg_field, visible)

    # ===============================================================
    def _loop(self):
        while self._loop_running:
            try:
                # HOME
                self._handle_slot(self.h1_time_field, self.h1_nr_field,
                                  self.h1_bg_field, self.h1_nr_bg_field)

                self._handle_slot(self.h2_time_field, self.h2_nr_field,
                                  self.h2_bg_field, self.h2_nr_bg_field)

                # AWAY
                self._handle_slot(self.a1_time_field, self.a1_nr_field,
                                  self.a1_bg_field, self.a1_nr_bg_field)

                self._handle_slot(self.a2_time_field, self.a2_nr_field,
                                  self.a2_bg_field, self.a2_nr_bg_field)

            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(0.6)
