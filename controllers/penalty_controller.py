import threading
import time


class PenaltyController:
    """
    Backend that manages all penalties using vMix text fields and countdowns.
    Mapping info is loaded from JSON.
    """

    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg

        mapping = cfg["mapping"]["penalties"]

        # HOME
        self.h1 = mapping["home"]["p1"]
        self.h2 = mapping["home"]["p2"]

        # AWAY
        self.a1 = mapping["away"]["p1"]
        self.a2 = mapping["away"]["p2"]

        # For internal time state
        self.state = {
            "home": {
                "p1": {"time": 0, "active": False},
                "p2": {"time": 0, "active": False},
            },
            "away": {
                "p1": {"time": 0, "active": False},
                "p2": {"time": 0, "active": False},
            },
        }

        # Background update loop
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    # ----------------------------------------------------------------------
    # INTERNAL LOOP
    # ----------------------------------------------------------------------
    def _loop(self):
        while self.running:
            try:
                # decrease each active timer
                for team in ["home", "away"]:
                    for slot in ["p1", "p2"]:
                        data = self.state[team][slot]
                        if not data["active"]:
                            continue
                        if data["time"] > 0:
                            data["time"] -= 1
                            self._apply_time(team, slot, data["time"])
                        if data["time"] <= 0:
                            data["active"] = False
                            self._hide(team, slot)

            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(1)

    # ----------------------------------------------------------------------
    # UI HELPERS
    # ----------------------------------------------------------------------
    def _apply_time(self, team, slot, seconds):
        m = seconds // 60
        s = seconds % 60
        text = f"{m:02d}:{s:02d}"

        mp = self._map(team, slot)
        self.client.set_text(
            self.cfg["inputs"]["penalty"],
            mp["time"],
            text
        )
        self._show(team, slot)

    def _map(self, team, slot):
        if team == "home":
            return self.h1 if slot == "p1" else self.h2
        return self.a1 if slot == "p1" else self.a2

    def _hide(self, team, slot):
        mp = self._map(team, slot)
        self.client.set_text_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["time"],
            False
        )
        self.client.set_text(
            self.cfg["inputs"]["penalty"],
            mp["number"],
            ""
        )
        self.client.set_bg_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["bg"],
            False
        )
        self.client.set_bg_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["nr_bg"],
            False
        )

    def _show(self, team, slot):
        mp = self._map(team, slot)
        self.client.set_text_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["time"],
            True
        )
        self.client.set_bg_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["bg"],
            True
        )
        self.client.set_bg_visible_on_or_off(
            self.cfg["inputs"]["penalty"],
            mp["nr_bg"],
            True
        )

    # ----------------------------------------------------------------------
    # PUBLIC METHODS FOR PANEL
    # ----------------------------------------------------------------------
    def adjust_penalty(self, team, slot, delta):
        data = self.state[team][slot]
        data["time"] = max(0, data["time"] + delta)
        if data["time"] > 0:
            data["active"] = True
            self._apply_time(team, slot, data["time"])
        else:
            data["active"] = False
            self._hide(team, slot)

    def clear_penalty(self, team, slot):
        data = self.state[team][slot]
        data["time"] = 0
        data["active"] = False
        self._hide(team, slot)

    def get_penalties(self):
        # UI refresh structure
        return self.state
