import threading
import time

class PenaltyController:
    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg
        self.mapping = cfg["mapping"]["penalties"]

        # local runtime model — avoids GUI bugs
        self.state = {
            "home": {
                "p1": {"seconds": 0, "active": False},
                "p2": {"seconds": 0, "active": False},
            },
            "away": {
                "p1": {"seconds": 0, "active": False},
                "p2": {"seconds": 0, "active": False},
            }
        }

        self._running = True
        self._loop_thread = threading.Thread(target=self._loop, daemon=True)
        self._loop_thread.start()

    # ============================================================
    # INTERNAL LOOP — KEEP PENALTIES SYNCED WITH CLOCK STATE
    # ============================================================
    def _loop(self):
        while self._running:
            try:
                # MAIN CLOCK TEXT
                main_input = self.cfg["inputs"]["scoreboard"]
                clock_field = self.cfg["mapping"]["scoreboard"]["clock"]
                clock_text = self.client.get_text(main_input, clock_field)

                main_running = (clock_text != "" and clock_text != "00:00")

                # sync visibility and running for all 4 penalties
                for team in ["home", "away"]:
                    for slot in ["p1", "p2"]:
                        data = self.state[team][slot]
                        if data["active"]:
                            # make visible
                            self._set_visible(team, slot, True)

                            # if main clock running → penalties must count down
                            if main_running:
                                self._pause(team, slot, False)
                            else:
                                self._pause(team, slot, True)
                        else:
                            # hide completely
                            self._set_visible(team, slot, False)
                            self._pause(team, slot, True)

            except Exception as e:
                print("[PenaltyController] loop error:", e)

            time.sleep(0.3)

    # ============================================================
    # SET PENALTY +10 / -10 / CLEAR
    # ============================================================
    def adjust_penalty(self, team, slot, delta_seconds):
        data = self.state[team][slot]
        data["seconds"] = max(0, data["seconds"] + delta_seconds)

        if data["seconds"] == 0:
            data["active"] = False
        else:
            data["active"] = True

        self._apply_time(team, slot)

    def clear_penalty(self, team, slot):
        data = self.state[team][slot]
        data["seconds"] = 0
        data["active"] = False
        self._apply_time(team, slot)

    # ============================================================
    # WRITE TIME TO VMIX FIELD AS MM:SS
    # ============================================================
    def _apply_time(self, team, slot):
        seconds = self.state[team][slot]["seconds"]
        mm = seconds // 60
        ss = seconds % 60
        txt = f"{mm:02}:{ss:02}"

        input_name = self.cfg["inputs"]["penalty"]
        field = self.mapping[team][slot]["time"]
        self.client.set_text(input_name, field, txt)

    # ============================================================
    # VISIBLE HELPERS
    # ============================================================
    def _set_visible(self, team, slot, visible):
        input_name = self.cfg["inputs"]["penalty"]

        time_field = self.mapping[team][slot]["time"]
        number_field = self.mapping[team][slot]["number"]
        bg_field = self.mapping[team][slot]["bg"]
        nrbg_field = self.mapping[team][slot]["nr_bg"]

        self.client.set_bg_visible_on_or_off(input_name, bg_field, visible)
        self.client.set_bg_visible_on_or_off(input_name, nrbg_field, visible)
        self.client.set_text_visible_on_or_off(input_name, time_field, visible)
        self.client.set_text_visible_on_or_off(input_name, number_field, visible)

    # ============================================================
    # PAUSE FUNCTION — IDENTICAL TO YOUR LEGACY SOLUTION
    # ============================================================
    def _pause(self, team, slot, pause):
        input_name = self.cfg["inputs"]["penalty"]
        time_field = self.mapping[team][slot]["time"]
        # vMix PauseCountdown TOGGLES — does not need True/False
        self.client.call_function("PauseCountdown", input=input_name, selected_name=time_field)


    # ============================================================
    # READABLE FOR GUI
    # ============================================================
    def get_penalties(self):
        return self.state

    # ============================================================
    # CLEANUP
    # ============================================================
    def stop(self):
        self._running = False
