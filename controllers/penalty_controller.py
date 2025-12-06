import time
import threading
from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.gui.player_select_dialog import PlayerSelectDialog


class PenaltyController:
    """
    Backend for managing hockey penalties.

    - Supports 2 HOME slots
    - Supports 2 AWAY slots
    - Slots store:
        active, duration, started_at, number, name
    - GUI calls get_penalties() to update the display
    - When the game clock pauses, all active penalties pause
    """

    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.cfg = config                # <<< REQUIRED FOR GUI COMPATIBILITY
        self.clock_running = False

        # 4 penalty slots — structured internal state
        self.penalties = {
            "home": [
                self._new_slot(),
                self._new_slot(),
            ],
            "away": [
                self._new_slot(),
                self._new_slot(),
            ]
        }

        # start watcher thread
        self._start_penalty_timer_thread()

    def _new_slot(self):
        """Return empty penalty slot structure"""
        return {
            "active": False,
            "duration": 0,      # seconds
            "remaining": 0,     # seconds
            "last_tick": 0,
            "number": "",
            "name": "",
        }

    # ----------------------------------------------------------------------
    # LIVE PENALTY INSERTION
    # ----------------------------------------------------------------------

    def start_penalty(self, parent_tk, team: str, slot_index: int):
        """
        Called when operator clicks a penalty slot button in the GUI.
        """
        # Determine which lineup input to use
        if team == "home":
            lineup_input = self.config.get("penalty_players", {}).get("home_input", "")
        else:
            lineup_input = self.config.get("penalty_players", {}).get("away_input", "")

        # Open selection dialog
        dlg = PlayerSelectDialog(parent_tk, lineup_input)
        result = dlg.run()
        if not result:
            return

        duration_minutes = result["duration"]
        seconds = duration_minutes * 60

        slot = self.penalties[team][slot_index]
        slot["active"] = True
        slot["duration"] = seconds
        slot["remaining"] = seconds
        slot["last_tick"] = time.time()
        slot["number"] = result["number"]
        slot["name"] = result["name"]

        # update graphics
        self._apply_to_vmix(team, slot_index)

    # ----------------------------------------------------------------------
    # CLOCK SYNC
    # ----------------------------------------------------------------------

    def set_clock_running(self, running: bool):
        self.clock_running = running

    # ----------------------------------------------------------------------
    # BACKGROUND TIMER THREAD
    # ----------------------------------------------------------------------

    def _start_penalty_timer_thread(self):
        t = threading.Thread(target=self._timer_loop, daemon=True)
        t.start()

    def _timer_loop(self):
        """
        Runs forever, ticking penalties every second
        """
        while True:
            time.sleep(1)
            if not self.clock_running:
                continue

            now = time.time()

            # update all slots
            for team in ["home", "away"]:
                for i in range(2):
                    slot = self.penalties[team][i]
                    if not slot["active"]:
                        continue

                    delta = now - slot["last_tick"]
                    slot["last_tick"] = now
                    slot["remaining"] -= delta

                    if slot["remaining"] <= 0:
                        self._clear_slot(team, i)
                    else:
                        self._update_time_to_vmix(team, i)

    # ----------------------------------------------------------------------
    # SLOT CLEARING
    # ----------------------------------------------------------------------

    def _clear_slot(self, team, i):
        slot = self.penalties[team][i]
        slot["active"] = False
        slot["remaining"] = 0
        slot["duration"] = 0

        mapping = self._mapping(team, i)

        # time text
        if mapping.get("field_time"):
            self.client.set_text(mapping["field_time"], "")

        # number text
        if mapping.get("field_number"):
            self.client.set_text(mapping["field_number"], "")

        # name text
        if mapping.get("field_name"):
            self.client.set_text(mapping["field_name"], "")

        # backgrounds hide
        if mapping.get("field_number_bg"):
            self.client.set_image_visible(mapping["field_number_bg"], False)
        if mapping.get("field_time_bg"):
            self.client.set_image_visible(mapping["field_time_bg"], False)

    # ----------------------------------------------------------------------
    # V-MIX UPDATES
    # ----------------------------------------------------------------------

    def _mapping(self, team, i):
        """
        Get mapping dict from config for slot:
            config["penalty"]["home"][0] or config["penalty"]["away"][1]
        """
        if "penalty" not in self.config:
            return {}
        return self.config["penalty"][team][i]

    def _apply_to_vmix(self, team, i):
        """
        Write player name/number/time to vMix fields
        """
        slot = self.penalties[team][i]
        mapping = self._mapping(team, i)

        # time field ON
        if mapping.get("field_time_bg"):
            self.client.set_image_visible(mapping["field_time_bg"], True)

        # write full time initially
        self._update_time_to_vmix(team, i)

        # write number if present
        if slot["number"] and mapping.get("field_number"):
            self.client.set_text(mapping["field_number"], slot["number"])
            if mapping.get("field_number_bg"):
                self.client.set_image_visible(mapping["field_number_bg"], True)
        else:
            if mapping.get("field_number"):
                self.client.set_text(mapping["field_number"], "")
            if mapping.get("field_number_bg"):
                self.client.set_image_visible(mapping["field_number_bg"], False)

        # write name if present
        if slot["name"] and mapping.get("field_name"):
            self.client.set_text(mapping["field_name"], slot["name"])
        else:
            if mapping.get("field_name"):
                self.client.set_text(mapping["field_name"], "")

    def _update_time_to_vmix(self, team, i):
        """
        Write countdown text to graphics
        """
        slot = self.penalties[team][i]
        mapping = self._mapping(team, i)

        secs = max(0, int(slot["remaining"]))
        mm = secs // 60
        ss = secs % 60
        txt = f"{mm:02}:{ss:02}"

        if mapping.get("field_time"):
            self.client.set_text(mapping["field_time"], txt)

    # ----------------------------------------------------------------------
    # GUI ACCESSOR
    # ----------------------------------------------------------------------

    def get_penalties(self):
        """
        GUI calls this to refresh penalty display.
        Returns dict with formatted strings.
        """
        display = {"home": [], "away": []}

        for team in ["home", "away"]:
            for slot in self.penalties[team]:
                if slot["active"]:
                    secs = max(0, int(slot["remaining"]))
                    mm = secs // 60
                    ss = secs % 60
                    txt = f"{mm:02}:{ss:02}"
                    display[team].append({
                        "active": True,
                        "time": txt,
                        "number": slot["number"],
                        "name": slot["name"],
                    })
                else:
                    display[team].append({
                        "active": False,
                        "time": "",
                        "number": "",
                        "name": "",
                    })

        return display
