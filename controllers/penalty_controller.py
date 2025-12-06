import threading
import time

class PenaltyController:
    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg

        # Input where penalties live
        self.input_name = cfg["inputs"]["penalty"]

        # JSON mapping fields
        mapping = cfg["mapping"]["penalties"]

        self.h1_time = mapping["home"]["p1"]["time"]
        self.h1_nr   = mapping["home"]["p1"]["number"]
        self.h1_bg   = mapping["home"]["p1"]["bg"]
        self.h1_nrbg = mapping["home"]["p1"]["nr_bg"]

        self.h2_time = mapping["home"]["p2"]["time"]
        self.h2_nr   = mapping["home"]["p2"]["number"]
        self.h2_bg   = mapping["home"]["p2"]["bg"]
        self.h2_nrbg = mapping["home"]["p2"]["nr_bg"]

        self.a1_time = mapping["away"]["p1"]["time"]
        self.a1_nr   = mapping["away"]["p1"]["number"]
        self.a1_bg   = mapping["away"]["p1"]["bg"]
        self.a1_nrbg = mapping["away"]["p1"]["nr_bg"]

        self.a2_time = mapping["away"]["p2"]["time"]
        self.a2_nr   = mapping["away"]["p2"]["number"]
        self.a2_bg   = mapping["away"]["p2"]["bg"]
        self.a2_nrbg = mapping["away"]["p2"]["nr_bg"]

        self.running = True

        # Start backend loop
        threading.Thread(target=self._loop, daemon=True).start()

    # -----------------------------
    # BACKEND LOOP
    # -----------------------------
    def _loop(self):
        while self.running:
            try:
                self._auto_hide()
            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(0.5)

    # -----------------------------
    # READ ALL PENALTIES FOR GUI
    # -----------------------------
    def get_penalties(self):
        """Return dict for GUI refresh"""
        return {
            "home": {
                "p1": {
                    "time": self.client.get_text(self.input_name, self.h1_time),
                    "nr":   self.client.get_text(self.input_name, self.h1_nr)
                },
                "p2": {
                    "time": self.client.get_text(self.input_name, self.h2_time),
                    "nr":   self.client.get_text(self.input_name, self.h2_nr)
                }
            },
            "away": {
                "p1": {
                    "time": self.client.get_text(self.input_name, self.a1_time),
                    "nr":   self.client.get_text(self.input_name, self.a1_nr)
                },
                "p2": {
                    "time": self.client.get_text(self.input_name, self.a2_time),
                    "nr":   self.client.get_text(self.input_name, self.a2_nr)
                }
            }
        }

    # -----------------------------
    # AUTO HIDE GRAPHICS IF 0
    # -----------------------------
    def _auto_hide(self):

        def handle(time_field, nr_field, bg_field, nrbg_field):
            t = self.client.get_text(self.input_name, time_field) or ""

            # visible?
            is_zero = (t.strip() in ["", "00:00", "0:00", "0", "0.0", "00.0"])
            visible = not is_zero

            # text
            self.client.set_text_visible_on_or_off(self.input_name, time_field, visible)
            self.client.set_text_visible_on_or_off(self.input_name, nr_field, visible)

            # background
            self.client.set_bg_visible_on_or_off(self.input_name, bg_field, visible)
            self.client.set_bg_visible_on_or_off(self.input_name, nrbg_field, visible)

        # HOME
        handle(self.h1_time, self.h1_nr, self.h1_bg, self.h1_nrbg)
        handle(self.h2_time, self.h2_nr, self.h2_bg, self.h2_nrbg)

        # AWAY
        handle(self.a1_time, self.a1_nr, self.a1_bg, self.a1_nrbg)
        handle(self.a2_time, self.a2_nr, self.a2_bg, self.a2_nrbg)
