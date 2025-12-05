import time
from typing import Dict, Optional

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.vmix_config import load_config


class PenaltyController:
    """
    Full automated penalty logic controller.

    Supported:
        - H1, H2, A1, A2 simultaneously
        - Auto countdown monitoring
        - Auto hide expired penalties
        - Auto multiview overlay alerts
        - State reading for GUI refresh
    """

    def __init__(self, client: VMixClient, cfg: dict):
        self.client = client
        self.cfg = cfg

        # Input name of scoreboard
        self.scoreboard_input = cfg["inputs"]["scoreboard"]

        # JSON field mapping
        self.fields = cfg["mapping"]["penalties"]
        # example:
        # self.fields["home"]["p1"]["time"]  → "HomeP1time.Text"

        # GUI refresh wants cache
        self._last_status = {}

        # Automation loop on/off
        self._run_auto = True

        # Start worker thread style
        self.client.set_tk_safe_update(False)
        self._start_background_poll()

    # -------------------------------------------------------------
    # Private helper
    # -------------------------------------------------------------

    def _start_background_poll(self):
        """
        Runs in background: monitor penalties and clock.
        """
        import threading
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    # -------------------------------------------------------------

    def _loop(self):
        while self._run_auto:
            try:
                self._auto_monitor()
            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(0.50)

    # -------------------------------------------------------------
    # AUTO MONITOR
    # -------------------------------------------------------------

    def _auto_monitor(self):
        """
        Detect expiry and auto hide fields.
        """
        status = self.get_all_penalty_status()

        for key, p in status.items():
            if not p["time_sec"]:
                continue

            if p["time_sec"] == 0:  # hide expired
                self._auto_hide_if_expired(key)

        # Optional — multiview alert:
        self._auto_multiview(status)

        self._last_status = status

    # -------------------------------------------------------------
    # AUTO HIDE logic
    # -------------------------------------------------------------

    def _auto_hide_if_expired(self, slot: str):
        """slot: 'H1', 'H2', 'A1', 'A2' """
        team = "home" if slot.startswith("H") else "away"
        p = "p1" if slot.endswith("1") else "p2"

        time_field = self.fields[team][p]["time"]
        nr_field = self.fields[team][p]["number"]
        bg_field = self.fields[team][p]["bg"]
        nr_bg_field = self.fields[team][p]["bg_number"]

        # hide everything
        self.client.set_text_visible(self.scoreboard_input, time_field, False)
        self.client.set_text_visible(self.scoreboard_input, nr_field, False)
        self.client.set_image_visible(self.scoreboard_input, bg_field, False)
        self.client.set_image_visible(self.scoreboard_input, nr_bg_field, False)

    # -------------------------------------------------------------
    # MULTIVIEW (HARD RULE)
    # -------------------------------------------------------------

    def _auto_multiview(self, status: dict):
        """
        Home alert if any H1 or H2 <=5 sec
        Away alert if any A1 or A2 <=5 sec
        """
        cfg = self.cfg["defaults"]
        mv_home = cfg.get("mv_home", None)
        mv_away = cfg.get("mv_away", None)

        if not mv_home or not mv_away:
            return  # optional feature

        # home
        if status["H1"]["time_sec"] and status["H1"]["time_sec"] <= 5:
            self.client.overlay_on(self.scoreboard_input, mv_home)
        elif status["H2"]["time_sec"] and status["H2"]["time_sec"] <= 5:
            self.client.overlay_on(self.scoreboard_input, mv_home)
        else:
            self.client.overlay_off(self.scoreboard_input, mv_home)

        # away
        if status["A1"]["time_sec"] and status["A1"]["time_sec"] <= 5:
            self.client.overlay_on(self.scoreboard_input, mv_away)
        elif status["A2"]["time_sec"] and status["A2"]["time_sec"] <= 5:
            self.client.overlay_on(self.scoreboard_input, mv_away)
        else:
            self.client.overlay_off(self.scoreboard_input, mv_away)

    # -------------------------------------------------------------
    # PENALTY READ
    # -------------------------------------------------------------

    def _read_slot(self, team: str, slot: str) -> dict:
        """
        Read GUI-friendly state for a single penalty.
        """
        fields = self.fields[team][slot]
        t = self.client.get_text(self.scoreboard_input, fields["time"]) or ""
        n = self.client.get_text(self.scoreboard_input, fields["number"]) or ""

        sec = self._parse_time_to_sec(t)

        return {
            "time": t,
            "time_sec": sec,
            "number": n,
        }

    @staticmethod
    def _parse_time_to_sec(txt: str) -> Optional[int]:
        """
        Convert MM:SS -> integer seconds
        """
        txt = txt.strip()
        if not txt:
            return None

        if ":" in txt:
            m, s = txt.split(":")
            try:
                return int(m) * 60 + int(s)
            except:
                return None

        try:
            return int(txt)
        except:
            return None

    # -------------------------------------------------------------
    # PUBLIC: GUI uses this
    # -------------------------------------------------------------

    def get_all_penalty_status(self) -> Dict[str, dict]:
        """
        Returns state object:
            {
                "H1": {"time","time_sec","number"},
                "H2": ...
                "A1": ...
                "A2": ...
            }
        """
        return {
            "H1": self._read_slot("home", "p1"),
            "H2": self._read_slot("home", "p2"),
            "A1": self._read_slot("away", "p1"),
            "A2": self._read_slot("away", "p2"),
        }

    # -------------------------------------------------------------
    # PUBLIC: Set or clear penalties (GUI buttons)
    # -------------------------------------------------------------

    def set_penalty(self, slot: str, number: str, duration_sec: int):
        """
        slot: "H1","H2","A1","A2"
        """
        team = "home" if slot.startswith("H") else "away"
        p = "p1" if slot.endswith("1") else "p2"

        fields = self.fields[team][p]

        mm = duration_sec // 60
        ss = duration_sec % 60
        txt = f"{mm:02d}:{ss:02d}"

        # Set values visible
        self.client.set_text(self.scoreboard_input, fields["time"], txt)
        self.client.set_text(self.scoreboard_input, fields["number"], number)

        self.client.set_text_visible(self.scoreboard_input, fields["time"], True)
        self.client.set_text_visible(self.scoreboard_input, fields["number"], True)
        self.client.set_image_visible(self.scoreboard_input, fields["bg"], True)
        self.client.set_image_visible(self.scoreboard_input, fields["bg_number"], True)

    def clear_penalty(self, slot: str):
        team = "home" if slot.startswith("H") else "away"
        p = "p1" if slot.endswith("1") else "p2"
        fields = self.fields[team][p]

        self.client.set_text(self.scoreboard_input, fields["time"], "")
        self.client.set_text(self.scoreboard_input, fields["number"], "")

        self.client.set_text_visible(self.scoreboard_input, fields["time"], False)
        self.client.set_text_visible(self.scoreboard_input, fields["number"], False)
        self.client.set_image_visible(self.scoreboard_input, fields["bg"], False)
        self.client.set_image_visible(self.scoreboard_input, fields["bg_number"], False)
