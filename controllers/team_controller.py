"""
TeamController – manages team names, logos, lineup bindings
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from scoreboard_app.core.vmix_client import VMixClient


class TeamController:
    """
    Handles team configuration and lineup data for home and away teams.

    Responsibilities:
    • update team names
    • update team logos
    • provide lineup details for other controllers
    • auto map to vMix fields via config
    """

    def __init__(self, client: VMixClient, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg
        self.mapping = cfg.get("mapping", {}).get("lineup", {})

        self.home_team: Dict[str, str] = {
            "name": "",
            "logo": ""
        }

        self.away_team: Dict[str, str] = {
            "name": "",
            "logo": ""
        }

    # ---------------------------------------------------------
    def set_home_name(self, name: str):
        """Update home team name text in vMix"""
        self.home_team["name"] = name
        field = self.mapping.get("home_teamname", "")
        if field:
            self.client.set_text(
                self.cfg["inputs"]["lineup_home"],
                field,
                name
            )

    # ---------------------------------------------------------
    def set_home_logo(self, url: str):
        """Update home team logo image"""
        self.home_team["logo"] = url
        field = self.mapping.get("home_logo", "")
        if field:
            self.client.set_image(
                self.cfg["inputs"]["lineup_home"],
                field,
                url
            )

    # ---------------------------------------------------------
    def set_away_name(self, name: str):
        """Update away team name text"""
        self.away_team["name"] = name
        field = self.mapping.get("away_teamname", "")
        if field:
            self.client.set_text(
                self.cfg["inputs"]["lineup_away"],
                field,
                name
            )

    # ---------------------------------------------------------
    def set_away_logo(self, url: str):
        """Update away team logo image"""
        self.away_team["logo"] = url
        field = self.mapping.get("away_logo", "")
        if field:
            self.client.set_image(
                self.cfg["inputs"]["lineup_away"],
                field,
                url
            )

    # ---------------------------------------------------------
    def get_home(self) -> Dict[str, str]:
        return self.home_team

    # ---------------------------------------------------------
    def get_away(self) -> Dict[str, str]:
        return self.away_team
