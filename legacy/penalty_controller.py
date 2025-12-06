# penalty_controller.py – Version 14.0
from typing import Dict, Any

from vmix_client import VMixClient


class PenaltyController:
    """
    Hanterar utvisningar:
      - set_penalty
      - clear_penalty
    Själva scoreboard-logiken ligger i ScoreboardController.
    """

    def __init__(self, client: VMixClient, config: Dict[str, Any]) -> None:
        self.client = client
        self.cfg = config
        self.sb_cfg = config["scoreboard"]
        self.sb_input = self.sb_cfg["input"]

    # ... (resten identisk med din nuvarande penalty_controller.py)
