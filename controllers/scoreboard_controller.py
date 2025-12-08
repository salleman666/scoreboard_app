import logging

from scoreboard_app.config.config_loader import load_config, save_config

class ScoreboardController:
    """
    Core scoreboard engine:
      - write home score, away score, time
      - used by goal/penalty/clock modules
    """

    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg
        self.mapping = cfg["mapping"]["scoreboard"]

        self.input = self.mapping.get("input", "")
        self.home_field = self.mapping.get("home", "")
        self.away_field = self.mapping.get("away", "")
        self.time_field = self.mapping.get("time", "")

    # ----------------------------------------------------------
    # Protect every VMix write: skip if field empty
    # ----------------------------------------------------------
    def _safe_set(self, field, value):
        if not self.input or not field:
            logging.error(f"[SCOREBOARD] Missing mapping: skip set {field}")
            return

        try:
            self.client.title_set_text(self.input, field, value)
        except Exception as e:
            logging.error(f"[SCOREBOARD] set {field} failed: {e}")

    # ----------------------------------------------------------
    # Score updates
    # ----------------------------------------------------------
    def set_home_score(self, score):
        self._safe_set(self.home_field, str(score))

    def set_away_score(self, score):
        self._safe_set(self.away_field, str(score))

    # ----------------------------------------------------------
    # Time updates
    # ----------------------------------------------------------
    def set_time(self, time_value):
        self._safe_set(self.time_field, time_value)

    # ----------------------------------------------------------
    # Mapping refresh (called after MappingDialog SAVE)
    # ----------------------------------------------------------
    def reload_mapping(self):
        cfg = load_config()
        self.cfg = cfg
        M = cfg["mapping"]["scoreboard"]

        self.input = M.get("input", "")
        self.home_field = M.get("home", "")
        self.away_field = M.get("away", "")
        self.time_field = M.get("time", "")
