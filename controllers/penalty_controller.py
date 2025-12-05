import threading
import time
from typing import Dict, Any


class PenaltyController:
    """
    Handles penalty state for:
      - home P1, P2
      - away P1, P2
    Reads/writes text fields in scoreboard input.
    """

    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg

        mapping = cfg["mapping"]["penalties"]

        # Field names — text timers
        self.h1_time = mapping["home"]["p1"]["time"]
        self.h2_time = mapping["home"]["p2"]["time"]
        self.a1_time = mapping["away"]["p1"]["time"]
        self.a2_time = mapping["away"]["p2"]["time"]

        # Player numbers
        self.h1_nr = mapping["home"]["p1"]["number"]
        self.h2_nr = mapping["home"]["p2"]["number"]
        self.a1_nr = mapping["away"]["p1"]["number"]
        self.a2_nr = mapping["away"]["p2"]["number"]

        # Background images — we use them to hide empty penalties
        self.h1_bg = mapping["home"]["p1"]["bg"]
        self.h2_bg = mapping["home"]["p2"]["bg"]
        self.a1_bg = mapping["away"]["p1"]["bg"]
        self.a2_bg = mapping["away"]["p2"]["bg"]

        # Number backgrounds
        self.h1_nr_bg = mapping["home"]["p1"]["nrbg"]
        self.h2_nr_bg = mapping["home"]["p2"]["nrbg"]
        self.a1_nr_bg = mapping["away"]["p1"]["nrbg"]
        self.a2_nr_bg = mapping["away"]["p2"]["nrbg"]

        # scoreboard input name
        self.input_name = cfg["inputs"]["scoreboard"]

        # start thread loop
        self._stop_loop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    # -----------------------
    # VMIX HELPER FUNCTIONS
    # -----------------------

    def _get_text(self, field: str) -> str:
        """Return a text value from scoreboard input."""
        return self.client.get_text(self.input_name, field)

    def _set_text(self, field: str, value: str):
        """Write a text value into scoreboard input."""
        return self.client.set_text(self.input_name, field, value)

    def _set_visible(self, name: str, visible: bool):
        """Toggle visibility of a field or image."""
        if visible:
            self.client.set_visible_on(self.input_name, name)
        else:
            self.client.set_visible_off(self.input_name, name)

    # -----------------------
    # PENALTY API
    # -----------------------

    def add_time(self, slot: str, seconds: int):
        """
        slot: "H1", "H2", "A1", "A2"
        seconds: positive or negative
        """
        field = {
            "H1": self.h1_time,
            "H2": self.h2_time,
            "A1": self.a1_time,
            "A2": self.a2_time,
        }.get(slot)

        if not field:
            return

        old = self._get_text(field)
        new_seconds = self._parse_time(old) + seconds
        if new_seconds < 0:
            new_seconds = 0

        self._set_text(field, self._format_time(new_seconds))

    def clear(self, slot: str):
        field = {
            "H1": self.h1_time,
            "H2": self.h2_time,
            "A1": self.a1_time,
            "A2": self.a2_time,
        }.get(slot)

        if not field:
            return

        self._set_text(field, "0:00")

    # -----------------------
    # DATA READOUT FOR GUI
    # -----------------------

    def get_penalties(self) -> Dict[str, Dict[str, Any]]:
        """Return current penalty state for GUI refresh."""
        def pack(name, nr_field, time_field):
            return {
                "number": self._get_text(nr_field),
                "time": self._get_text(time_field),
                "seconds": self._parse_time(self._get_text(time_field)),
            }

        return {
            "home": {
                "p1": pack("H1", self.h1_nr, self.h1_time),
                "p2": pack("H2", self.h2_nr, self.h2_time),
            },
            "away": {
                "p1": pack("A1", self.a1_nr, self.a1_time),
                "p2": pack("A2", self.a2_nr, self.a2_time),
            },
        }

    # -----------------------
    # AUTO VISIBILITY + CAMERA ALERTS
    # -----------------------

    def _loop(self):
        """Optional automatic hiding and overlay logic."""
        while not self._stop_loop:
            try:
                data = self.get_penalties()

                # automatically hide empty penalties
                for side in ["home", "away"]:
                    for pid in ["p1", "p2"]:
                        item = data[side][pid]
                        bg = getattr(self, f"{side[0]}{pid[1]}_bg")
                        nrbg = getattr(self, f"{side[0]}{pid[1]}_nr_bg")
                        time_field = getattr(self, f"{side[0]}{pid[1]}_time")

                        empty = (item["seconds"] == 0)
                        self._set_visible(time_field, not empty)
                        self._set_visible(bg, not empty)
                        self._set_visible(nrbg, not empty)

            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(0.5)

    # -----------------------
    # INTERNAL PARSERS
    # -----------------------

    @staticmethod
    def _parse_time(text: str) -> int:
        """Convert 'mm:ss' to seconds."""
        if not text or text.strip() == "":
            return 0
        try:
            if ":" in text:
                m, s = text.split(":")
                return int(m) * 60 + int(s)
            return int(text)
        except:
            return 0

    @staticmethod
    def _format_time(seconds: int) -> str:
        m = seconds // 60
        s = seconds % 60
        return f"{m}:{s:02d}"
