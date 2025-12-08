from scoreboard_app.controllers.base_controller import BaseController
import time

class GoalController(BaseController):
    """
    Handles goal registration:
    - sets scoreboard numbers
    - triggers goal popup
    - triggers after-goal graphics
    """
    def __init__(self, client, cfg):
        super().__init__(client, cfg)

        self.cfg = cfg
        self.client = client

    # ----------------------------------------------------------------------
    def add_goal(self, team, number, name):
        """
        Called from PlayerSelectDialog via goal_panel.py
        team = "home" | "away"
        number = jersey number as string
        name = scorer name as string
        """

        if not team:
            return

        # READ SCORE
        if team == "home":
            hs = int(self.get("score.home") or 0) + 1
            self.set("score.home", hs)
        else:
            as_ = int(self.get("score.away") or 0) + 1
            self.set("score.away", as_)

        # UPDATE SCOREBOARD TITLE
        self._push_score()

        # SHOW GOAL POPUP (if configured)
        self._show_goal_popup(team)

        # SHOW SCORER GRAPHICS (if configured)
        self._show_after_goal(team, number, name)

    # ----------------------------------------------------------------------
    def _push_score(self):
        """
        Update scoreboard GT fields via vmix_client
        """
        m = self.cfg

        if not m.get("score.input"):
            return

        inp = m["score.input"]

        # home
        if m.get("score.home_field") and self.get("score.home") is not None:
            self.client.set_text(
                inp,
                m["score.home_field"],
                str(self.get("score.home"))
            )

        # away
        if m.get("score.away_field") and self.get("score.away") is not None:
            self.client.set_text(
                inp,
                m["score.away_field"],
                str(self.get("score.away"))
            )

    # ----------------------------------------------------------------------
    def _show_goal_popup(self, team):
        """
        Use GOAL pop-up overlay settings
        """
        m = self.cfg
        if not m.get("goal.popup_input"):
            return

        inp = m["goal.popup_input"]
        ov = int(m.get("goal.popup_overlay") or 1)
        dur = int(m.get("goal.popup_duration") or 3000)

        # show popup
        self.client.overlay_on(inp, ov)
        time.sleep(dur / 1000.0)
        self.client.overlay_off(inp, ov)

    # ----------------------------------------------------------------------
    def _show_after_goal(self, team, number, name):
        """
        Display scorer graphics after goal
        """
        m = self.cfg

        if not m.get("goal.after_input"):
            return

        inp = m["goal.after_input"]
        ov = int(m.get("goal.after_overlay") or 1)
        dur = int(m.get("goal.after_duration") or 3000)
        pause = int(m.get("goal.after_pause") or 1000)

        # UPDATE TITLE FIELDS
        # only update those configured in MappingDialog
        if number and m.get("goal.after_number_field"):
            self.client.set_text(inp, m["goal.after_number_field"], number)

        if name and m.get("goal.after_name_field"):
            self.client.set_text(inp, m["goal.after_name_field"], name)

        if team and m.get("goal.after_team_field"):
            self.client.set_text(inp, m["goal.after_team_field"], team.upper())

        # show overlay
        self.client.overlay_on(inp, ov)
        time.sleep(dur / 1000.0)
        self.client.overlay_off(inp, ov)
        time.sleep(pause / 1000.0)
