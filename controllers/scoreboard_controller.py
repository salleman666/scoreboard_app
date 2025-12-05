from typing import Optional, Dict, Any
from scoreboard_app.core.vmix_client import VMixClient


class ScoreboardController:
    """
    High-level API for updating scoreboard-related graphics on vMix.

    This controller is responsible for:
    - Score updates
    - Team names
    - Logos
    - Overlay control
    - Empty goal graphics (home/away)

    It uses VMixClient as backend for TCP control.
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]) -> None:
        """
        Args:
            client: Active VMixClient instance
            cfg: Parsed config dict loaded from vmix_config.json
        """
        self.client = client
        self.cfg = cfg

    # ------------------------------------------------------------
    # SCORE UPDATES
    # ------------------------------------------------------------
    def set_score(self, home: int, away: int) -> bool:
        """
        Update scoreboard score values.

        Args:
            home: home team score
            away: away team score

        Returns:
            True if both fields sent successfully
        """
        board = self.cfg["scoreboard"]
        input_name = board["input"]

        ok1 = self.client.set_text(input_name, board["home_score_field"], str(home))
        ok2 = self.client.set_text(input_name, board["away_score_field"], str(away))
        return ok1 and ok2

    # ------------------------------------------------------------
    # TEAM NAMES
    # ------------------------------------------------------------
    def set_team_names(self, home_name: str, away_name: str) -> bool:
        """
        Set team names shown on scoreboard input.

        Args:
            home_name: name for home team
            away_name: name for away team

        Returns:
            True on full success
        """
        board = self.cfg["scoreboard"]
        input_name = board["input"]

        ok1 = self.client.set_text(input_name, board["home_team_field"], home_name)
        ok2 = self.client.set_text(input_name, board["away_team_field"], away_name)
        return ok1 and ok2

    # ------------------------------------------------------------
    # TEAM LOGOS
    # ------------------------------------------------------------
    def set_team_logos(self, home_logo: str, away_logo: str) -> bool:
        """
        Set team logos for scoreboard.

        Args:
            home_logo: path or URL to home team logo
            away_logo: path or URL to away team logo

        Returns:
            True if both set successfully
        """
        board = self.cfg["scoreboard"]
        input_name = board["input"]

        ok1 = self.client.set_source(input_name, board["home_logo_field"], home_logo)
        ok2 = self.client.set_source(input_name, board["away_logo_field"], away_logo)
        return ok1 and ok2

    # ------------------------------------------------------------
    # OVERLAY CONTROL
    # ------------------------------------------------------------
    def show_scoreboard(self) -> bool:
        """
        Show scoreboard input as overlay 1 (default)
        """
        overlay = self.cfg["scoreboard"]["overlay"]
        return self.client.set_overlay(overlay, self.cfg["scoreboard"]["input"])

    def hide_scoreboard(self) -> bool:
        """
        Hide scoreboard overlay channel
        """
        overlay = self.cfg["scoreboard"]["overlay"]
        return self.client.clear_overlay(overlay)

    # ------------------------------------------------------------
    # EMPTY GOAL GRAPHICS
    # ------------------------------------------------------------
    def set_empty_goal_home(self, enabled: bool) -> bool:
        """
        Display / clear empty goal indicator for home team.

        Args:
            enabled: True = show graphic, False = hide

        Returns:
            True on success
        """
        goal = self.cfg["emptygoal"]
        field = goal["home_field"]

        if enabled:
            return self.client.set_text(goal["input"], field, goal["home_text"])
        else:
            return self.client.set_text(goal["input"], field, goal["blank_text"])

    def set_empty_goal_away(self, enabled: bool) -> bool:
        """
        Display / clear empty goal indicator for away team.

        Args:
            enabled: True = show graphic, False = hide

        Returns:
            True on success
        """
        goal = self.cfg["emptygoal"]
        field = goal["away_field"]

        if enabled:
            return self.client.set_text(goal["input"], field, goal["away_text"])
        else:
            return self.client.set_text(goal["input"], field, goal["blank_text"])
