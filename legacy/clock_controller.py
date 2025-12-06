# clock_controller.py – Version 14.0
from typing import Dict, Any, Optional

from vmix_client import VMixClient


def _parse_time_to_seconds(t: str) -> Optional[int]:
    """
    Tar t.ex. '20:00', '20.00', '0:05', '60.0', '5', '' och returnerar sekunder eller None.
    Används för att avgöra om vi ska justera en timer (> 0 sek).
    """
    if t is None:
        return None
    t = str(t).strip()
    if not t:
        return None

    if t in ("0", "00", "00:00", "0:00", "0.0", "00.0"):
        return 0

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

    if "." in t:
        try:
            v = float(t.replace(" ", ""))
            if v < 0:
                return None
            return int(v)
        except ValueError:
            return None

    try:
        v = int(t.replace(" ", ""))
        if v < 0:
            return None
        return v
    except ValueError:
        return None


def _format_mmss(secs: int) -> str:
    if secs < 0:
        secs = 0
    m = secs // 60
    s = secs % 60
    return f"{m:02d}:{s:02d}"


class ClockController:
    """
    Separat klock-controller (används i vissa versioner).
    """

    def __init__(self, client: VMixClient, config: Dict[str, Any]) -> None:
        self.client = client
        self.cfg = config
        self.sb_cfg = config["scoreboard"]
        self.sb_input = self.sb_cfg["input"]

    def _scoreboard_input_number(self) -> str:
        num = self.client.find_input_number(self.sb_input)
        if num is None:
            raise RuntimeError(f"Kunde inte hitta scoreboard-input: {self.sb_input}")
        return num

    def set_match_time(self, time_str: str) -> None:
        secs = _parse_time_to_seconds(time_str)
        if secs is None or secs < 0:
            raise ValueError(f"Ogiltig tid: {time_str!r}")
        t_str = _format_mmss(secs)

        inp = self._scoreboard_input_number()
        clock_field = self.sb_cfg["clock_field"]

        self.client.call_function("StopCountdown", Input=inp, SelectedName=clock_field)
        self.client.call_function("SetCountdown", Input=inp, SelectedName=clock_field, Value=t_str)
        self.client.set_text(inp, clock_field, t_str)

    # ... (övriga metoder oförändrade från din 13.x-fil)
