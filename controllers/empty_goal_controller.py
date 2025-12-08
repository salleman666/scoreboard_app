import logging

log = logging.getLogger(__name__)


class EmptyGoalController:
    """
    Handles empty-net indicators for HOME and AWAY.
    """

    def __init__(self, client, cfg):
        """
        client -> VMixClient
        cfg -> full config dictionary
        """
        self.client = client
        self.cfg = cfg

        self.mapping = cfg["mapping"]["empty_goal"]
        self.input = self.mapping["input"]
        self.fields = self.mapping["fields"]

        # internal state
        self.home_state = False
        self.away_state = False

    # ======================================================
    # PUBLIC SWITCHES
    # ======================================================
    def toggle_home(self):
        self.home_state = not self.home_state
        self._render_home()

    def toggle_away(self):
        self.away_state = not self.away_state
        self._render_away()

    def set_home(self, state: bool):
        self.home_state = bool(state)
        self._render_home()

    def set_away(self, state: bool):
        self.away_state = bool(state)
        self._render_away()

    # ======================================================
    # INTERNAL FIELD UPDATES
    # ======================================================
    def _render_home(self):
        text_field = self.fields.get("home_text", "")
        bg_field = self.fields.get("home_bg", "")

        if text_field:
            # text visible if state true else blank
            value = "EMPTY GOAL" if self.home_state else ""
            self._set_field_safe(text_field, value)

        if bg_field:
            # 1=on, 0=off
            vis = "1" if self.home_state else "0"
            self._set_field_safe(bg_field, vis)

    def _render_away(self):
        text_field = self.fields.get("away_text", "")
        bg_field = self.fields.get("away_bg", "")

        if text_field:
            value = "EMPTY GOAL" if self.away_state else ""
            self._set_field_safe(text_field, value)

        if bg_field:
            vis = "1" if self.away_state else "0"
            self._set_field_safe(bg_field, vis)

    # ======================================================
    def _set_field_safe(self, field, value):
        if not field:
            return

        try:
            self.client.title_set_text(self.input, field, str(value))
        except Exception as e:
            log.error(f"[EMPTY GOAL] failed field={field} val={value}: {e}")
