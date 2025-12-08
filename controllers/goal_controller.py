import logging
from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.controllers.scoreboard_controller import ScoreboardController

log = logging.getLogger(__name__)


class GoalController:
    """
    Handles:
        - register goal
        - update scoreboard score
        - trigger goal popup overlay
        - trigger scorer graphics overlay
        - automatic mapping stored in config:
        
        cfg["mapping"]["goals"] = {
            "goal_popup": {
                "input": "...",
                "overlay": 1,
                "duration_ms": 2000
            },
            "after_goal": {
                "input": "...",
                "overlay": 2,
                "duration_ms": 3000,
                "fields": {
                    "name": "...",
                    "number": "...",
                    "team": "...",
                    "logo": "..."
                }
            }
        }
    """

    def __init__(self, client: VMixClient, cfg: dict, scoreboard: ScoreboardController):
        self.client = client
        self.cfg = cfg
        self.scoreboard = scoreboard

        self._resolve_mapping()

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    def _resolve_mapping(self):
        gm = self.cfg.get("mapping", {}).get("goals", {})

        # GOAL POPUP BLOCK
        p = gm.get("goal_popup", {})
        self.popup_input = p.get("input")
        self.popup_overlay = p.get("overlay", 1)
        self.popup_duration = p.get("duration_ms", 2000)

        # SCORER BLOCK
        a = gm.get("after_goal", {})
        self.after_input = a.get("input")
        self.after_overlay = a.get("overlay", 2)
        self.after_duration = a.get("duration_ms", 3000)

        # scorer field mapping
        self.after_fields = a.get("fields", {
            "name": None,
            "number": None,
            "team": None,
            "logo": None,
        })

        log.info("[GOAL] mapping resolved")

    # -------------------------------------------------
    # REGISTER GOAL
    # GUI calls:
    #   goal_controller.register_goal("home", player_name, number, logo, team)
    # -------------------------------------------------
    def register_goal(self, side: str,
                      player_name=None,
                      player_number=None,
                      team_name=None,
                      logo_url=None):
        """
        MAIN ENTRY POINT FOR GOAL EVENT
        """

        if side == "home":
            self.scoreboard.inc_home(1)
        else:
            self.scoreboard.inc_away(1)

        # Always fire goal popup overlay
        self._show_goal_popup()

        # Only show scorer graphics IF we have enough data
        if player_name or player_number or team_name or logo_url:
            self._show_after_goal(player_name, player_number, team_name, logo_url)

    # -------------------------------------------------
    # GOAL POPUP OVERLAY
    # -------------------------------------------------
    def _show_goal_popup(self):
        if not self.popup_input:
            log.error("[GOAL] Missing mapping: goal_popup.input")
            return

        try:
            # SHOW
            self.client.overlay_on(self.popup_input, self.popup_overlay)
            self.client.after_delay(self.popup_duration,
                                    lambda: self.client.overlay_off(self.popup_input, self.popup_overlay))
        except Exception as e:
            log.error(f"[GOAL] popup overlay failed: {e}")

    # -------------------------------------------------
    # AFTER GOAL — PLAYER GRAPHICS
    # -------------------------------------------------
    def _show_after_goal(self, name, number, team, logo):
        if not self.after_input:
            log.error("[GOAL] Missing mapping: after_goal.input")
            return

        # PUSH fields only if mapped + non-empty
        try:
            if name and self.after_fields.get("name"):
                self.client.update_text(self.after_input, self.after_fields["name"], name)

            if number and self.after_fields.get("number"):
                self.client.update_text(self.after_input, self.after_fields["number"], str(number))

            if team and self.after_fields.get("team"):
                self.client.update_text(self.after_input, self.after_fields["team"], team)

            if logo and self.after_fields.get("logo"):
                self.client.update_text(self.after_input, self.after_fields["logo"], logo)

        except Exception as e:
            log.error(f"[GOAL] field update failed: {e}")

        # SHOW AFTER-GOAL OVERLAY
        try:
            self.client.overlay_on(self.after_input, self.after_overlay)

            self.client.after_delay(self.after_duration,
                                    lambda: self.client.overlay_off(self.after_input, self.after_overlay))

        except Exception as e:
            log.error(f"[GOAL] after-goal overlay failed: {e}")
