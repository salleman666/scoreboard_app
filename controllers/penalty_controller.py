import logging

log = logging.getLogger(__name__)


class PenaltyController:
    """
    NEW PENALTY CONTROLLER USING:
    - native vMix countdown for each slot
    - automatic sync with scoreboard clock (if clock provided)
    - show/hide BG + number fields from mapping
    """

    def __init__(self, vmix_client, config, clock_controller=None):
        self.vmix = vmix_client
        self.cfg = config
        self.clock = clock_controller  # <-- OPTIONALLY AVAILABLE

        self.mapping = self.cfg.get("mapping", {}).get("penalties", {})

        # Expected structure from mapping dialog:
        # penalties:
        #   home:
        #     slot1: { input, time, timebg, number, numberbg }
        #     slot2: { ... }
        #   away:
        #     slot1: { ... }
        #     slot2: { ... }

        self.slots = {
            "home": self.mapping.get("home", {}),
            "away": self.mapping.get("away", {}),
        }

    # =======================================================
    # HELPERS
    # =======================================================
    def _slot_items(self, side):
        slots = self.slots.get(side, {})
        for k, v in slots.items():
            yield k, v

    # =======================================================
    # START PENALTY
    # =======================================================
    def start_penalty(self, side, slot_id, duration_seconds, player_number=None):
        slot = self.slots.get(side, {}).get(slot_id)
        if not slot:
            return

        inp = slot.get("input")
        if not inp:
            return

        mm = duration_seconds // 60
        ss = duration_seconds % 60
        value = f"{mm:02}:{ss:02}"

        log.info(f"[PENALTY] Start slot {side}/{slot_id} duration={value}")
        self.vmix.set_countdown(inp, value)
        self.vmix.start_countdown(inp)

        # PLAYER NUMBER
        if player_number is not None:
            num_field = slot.get("number")
            bg_field = slot.get("numberbg")
            if num_field:
                self.vmix.set_text(inp, num_field, str(player_number))
                self.vmix.set_text_visible(inp, num_field, True)
            if bg_field:
                self.vmix.set_image_visible(inp, bg_field, True)
        else:
            # NO NUMBER — ONLY SHOW TIME BG
            bg_field = slot.get("timebg")
            if bg_field:
                self.vmix.set_image_visible(inp, bg_field, True)

    # =======================================================
    # STOP PENALTY
    # =======================================================
    def stop_penalty(self, side, slot_id):
        slot = self.slots.get(side, {}).get(slot_id)
        if not slot:
            return

        inp = slot.get("input")
        if not inp:
            return

        log.info(f"[PENALTY] Stop {side}/{slot_id}")
        self.vmix.stop_countdown(inp)

    # =======================================================
    # CLEAR PENALTY
    # =======================================================
    def clear_penalty(self, side, slot_id):
        slot = self.slots.get(side, {}).get(slot_id)
        if not slot:
            return

        inp = slot.get("input")
        if not inp:
            return

        log.info(f"[PENALTY] Clear {side}/{slot_id}")
        self.vmix.set_countdown(inp, "00:00")
        self.vmix.stop_countdown(inp)

        # HIDE FIELDS
        for f in ["timebg", "numberbg", "number"]:
            name = slot.get(f)
            if name:
                # Detect text vs image
                if "Source" in name:
                    self.vmix.set_image_visible(inp, name, False)
                else:
                    self.vmix.set_text_visible(inp, name, False)

    # =======================================================
    # GLOBAL SYNC
    # =======================================================
    def pause_all(self):
        """
        Called when scoreboard clock pauses.
        If no clock provided → skip silently.
        """
        if not self.clock:
            return

        for side in ["home", "away"]:
            for slot_id, slot in self.slots.get(side, {}).items():
                inp = slot.get("input")
                if inp:
                    self.vmix.stop_countdown(inp)

    def resume_all(self):
        """
        Called when scoreboard clock resumes.
        If no clock provided → skip silently.
        """
        if not self.clock:
            return

        for side in ["home", "away"]:
            for slot_id, slot in self.slots.get(side, {}).items():
                inp = slot.get("input")
                if inp:
                    self.vmix.start_countdown(inp)

    # =======================================================
    # GUI STATUS
    # =======================================================
    def get_penalties(self):
        """
        GUI polling status:
        - read remaining time for each slot
        """
        result = {"home": {}, "away": {}}

        for side in ["home", "away"]:
            for slot_id, slot in self.slots.get(side, {}).items():
                inp = slot.get("input")
                time_field = slot.get("time")

                if not inp or not time_field:
                    result[side][slot_id] = {"time": ""}
                else:
                    txt = self.vmix.get_text(inp, time_field)
                    result[side][slot_id] = {"time": txt}

        return result
