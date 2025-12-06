# graphics_controller.py – Version 14.0
import threading
import time
from typing import Dict, Any, Optional

from vmix_client import VMixClient


def _parse_time_to_seconds(t: str) -> Optional[int]:
    """
    Tar t.ex. '20:00', '0:05', '60.0', '5', '' och returnerar sekunder eller None.
    """
    if t is None:
        return None
    t = str(t).strip()
    if not t:
        return None
    if ":" in t:
        parts = t.replace(" ", "").split(":")
        if len(parts) == 2:
            try:
                m = int(parts[0])
                s = int(parts[1])
                if m < 0 or s < 0:
                    return None
                return m * 60 + s
            except ValueError:
                return None
    try:
        return int(float(t))
    except ValueError:
        return None


class GraphicsController:
    """
    Hanterar mål-grafik, efter-mål-grafik m.m.
    (Logiken är densamma som i din 13.x-version, bara headern uppdaterad.)
    """

    def __init__(self, client: VMixClient, config: Dict[str, Any]) -> None:
        self.client = client
        self.cfg = config
        self.sb_cfg = config.get("scoreboard", {})

    # ... (övriga metoder exakt som i din befintliga graphics_controller.py)
